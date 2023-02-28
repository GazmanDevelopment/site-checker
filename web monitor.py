import json
import logging
import os
import requests
import sys
import urllib

from configparser import ConfigParser
from logging.handlers import RotatingFileHandler
from requests.utils import requote_uri

SETTINGS_FILE = 'settings.ini'
log = ''
site_file = ''
site_list = ''
api_url = ''
api_user = ''
api_pass = ''
api_from = ''
sms_to = ''

def init():
    # Clear the terminal window during debugging, just makes life easier
    os.system('cls' if os.name == 'nt' else 'clear')
    global site_file, site_list, api_url, api_pass, api_user, api_from, sms_to, log

    # Load the config file
    config = ConfigParser()
    if os.path.isfile(SETTINGS_FILE):
        config.read(SETTINGS_FILE)
    else:
        sys.exit("Settings file not located - exiting program")

    # Load Global variables from config
    site_file   = config.get('ENVIRONMENT', 'site_list')
    api_url     = config.get('SMS', 'api_url')
    api_user    = config.get('SMS', 'api_user')
    api_pass    = config.get('SMS', 'api_pass')
    api_from    = config.get('SMS', 'api_from')
    sms_to      = config.get('SMS', 'sms_to')

    # Load local variables from config
    log_file    = config.get('ENVIRONMENT', 'log_file')
    max_bytes = int(config.get('ENVIRONMENT', 'log_max_bytes'))
    max_log_files = int(config.get('ENVIRONMENT', 'log_backups'))

    # Define the format for logs as <TIME> - <ERROR LEVEL>: <Log Message>
    log_formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')

    # Create a rotating log handler.  When the log file reaches the maximum size defined, it is rolled over to a <log name>.log.x name
    rotate_handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=max_log_files, mode='a', delay=False)
    rotate_handler.setFormatter(log_formatter)
    rotate_handler.setLevel(logging.INFO)

    # Setup the actual log variable that will be used by the app
    log = logging.getLogger('root')
    log.setLevel(logging.INFO)
    log.addHandler(rotate_handler)

    print('Test Environment: ', config.get('ENVIRONMENT', 'test_environment'))
    log.info("*******************************")
    log.info("**** Commencing Site Check ****")
    log.info("*******************************")
    log.info('---- Config Loaded ----')
    log.info('Test Environment: ' + config.get('ENVIRONMENT', 'test_environment'))

    return True

def load_sites():
    log.info('---- Loading Site List ----')
    # Try opening the list of sites to check.  This should be a JSON encoded list of sites
    # See the sample JSON file for correct format
    try:
        with open(site_file, 'r') as f:
            global site_list 
            site_list = json.loads(f.read())
            f.close()
        log.info('---- Site List Loaded ----')
        
        return True
    except Exception as e:
        log.error('Error loading site list: ' + str(e))
        log.error('---- Exiting Program ----')
        sys.exit("Error loading site list - exiting program")

def test_sites():
    log.info('---- Commencing Site Checks ----')

    # Loop through each website and try to load it.  If we can, check the response for the string provided.  We also check the prior status
    # and if there has been a change, we send an SMS and write this out for next time.
    for website in site_list:
        log.info('Checking Site: ' + website['site'] + ' (' + website['url'] + ').  Last Check Status: ' + str(website['last_check']))

        try:
            # Read the current values from the JSON object
            url_to_check    = website['url']
            text_to_locate  = website['search_string']
            site_name       = website['site']
            last_check_status = website['last_check']

            # Clear any previous values
            site_content = ''
            site_response = ''

            # Try to connect to the site and read the response into a string object            
            site_response = urllib.request.urlopen(url_to_check)
            site_content = site_response.read().decode(site_response.headers.get_content_charset())

            # Check to see if the search string is in the response
            status = text_to_locate in site_content

            # If we were able to connect to the site, check to see if the status has changed.  Rules for status:
            #   If we can find the search string, the Status is TRUE
            #   If we are unable to find the search string, the Status is FALSE
            if status == last_check_status:
                print(site_name, url_to_check, status, 'No Status Change')
            else:
                print(site_name, url_to_check, status, 'Status Change')
                send_message(site_name, status, last_check_status)

            # Update the JSON object with the last test status.  This will be saved back to the file and used next round
            website['last_check'] = status
        except Exception as e:
            # If there is any error communicating with the site, the Status is always FALSE, but we still need to check it
            # against what the last Status was
            if False == last_check_status:
                print(site_name, url_to_check, False, 'No Status Change')
            else:
                print(site_name, url_to_check, False, 'Status Change')
                send_message(site_name, False, last_check_status)
            
            # Update the JSON object with the last test status.  This will be saved back to the file and used next round
            website['last_check'] = False

def send_message(site, status, old_status):
    # This script is designed to work with the API from SMS Broadcast.  You will need to adjust the URL for whatever service you use
    # Note that SMS Broadcast is a paid service and you will need an account.
    # Follow instructions here to setup the API: https://support.smsbroadcast.com.au/hc/en-us/articles/4413677982607-How-to-Create-New-API-Credentials
    log.info('---- Sending Status Change Notification: ' + site + ' ----')
    # Determine the status change (up to down, down to up)
    current_status = 'up' if status else 'down'
    prior_status = 'up' if old_status else 'down'
    log.info('Status change to: ' + current_status)

    # Build the message.  Keep it simple, stupid!
    message = "Service Status Change: " + site + ".  Status changed from " + prior_status + " to " + current_status + "."
    log.info('Message built: ' + message)

    # Build the request URL and encode it
    api_request = requote_uri(api_url + "?username=" + api_user + "&password=" + api_pass + "&from=" + api_from +  "&to=" + sms_to + "&message=" + message)
    log.info('API Request built and encoded')

    # Actually send the request
    r = requests.get(api_request)
    log.info('Request sent: ' + str(r))
    
    log.info('---- End Status Change Notification: ' + site + ' ----')

def write_status():
    # Write the JSON data back.  This will include the status of the website for this round of checks.  This will be used as the "last status"
    # value the next time this process runs.
    log.info('---- Writing Site Check Results ----')
    with open(site_file, 'w') as f:
        json.dump(site_list, f, ensure_ascii=False, indent=4)
        f.close()
    log.info('---- Writing Status Done ----')

if __name__ == "__main__":
    if init():
        load_sites()
        test_sites()
        write_status()