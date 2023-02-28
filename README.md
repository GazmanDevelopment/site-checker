# Python Site Checker
A simple Python script to check a list of websites and determine their status.  If the status has changed since the last check, the code sends an SMS to a list of recipients using the [SMS Broadcast](https://app.smsbroadcast.com.au) service.

## Requirements
- Python 3+
- Account with credit at SMS Broadcast
- API Credentials at SMS Broadcast [How to Create New API Credentials](https://support.smsbroadcast.com.au/hc/en-us/articles/4413677982607-How-to-Create-New-API-Credentials)

## Setup
- Download all files into a folder on your machine
- Edit the *settings.ini* file tos uit your environment
  - At thevery least you will need to enter:
    - Your SMS Broadcast API User Details
    - Name of Sender
    - SMS REcipient(s).  If entering multiple recipients, use a comma to separate them with no spaces. *eg* 0416123456,0415987654
