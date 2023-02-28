# Python Site Checker
A simple Python script to check a list of websites and determine their status.  If the status has changed since the last check, the code sends an SMS to a list of recipients using the [SMS Broadcast](https://app.smsbroadcast.com.au) service.

## Requirements
- Python 3+
- Account with credit at SMS Broadcast
- API Credentials at SMS Broadcast [How to Create New API Credentials](https://support.smsbroadcast.com.au/hc/en-us/articles/4413677982607-How-to-Create-New-API-Credentials)

## Setup
- Download all files into a folder on your machine
- Edit the `settings.ini` file tos uit your environment
  - At the very least you will need to enter:
    - Your SMS Broadcast API User Details
    - Name of Sender
    - SMS Recipient(s).  If entering multiple recipients, use a comma to separate them with no spaces. *eg* `0416123456,0415987654`
  - Review the logging settings
  - The Test Environment is not currently used
    - A future update will have the code check this, and if running in test it will not send the SMS but will complete all other actions
- Add your websites / services to the `websites.json` file
  - The JSON format must be retained
  - Try to avoid including HTML formatting and other special characters, the code doesn't seem to like it
  - Ensure the text in the `search_string` setting **_only_** appears when the site is running and available
- Configure the script to run on a schedule that suits your needs
  - The steps for this will vary depending on which system (Linux vs. Windows) you use and how you have Python installed etc
