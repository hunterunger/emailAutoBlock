![Screenshot](screenshot.jpg)

A very simple program that automatically deletes blocked emails and/or auto-replies.

## ⏱ Quick Start
Tested on Python 3.8. 
Simply run this from the terminal get started:
```
git clone https://github.com/hunterunger/emailAutoBlock.git
cd emailAutoBlock
python3 -m pip install -r requirements.txt
python3 main.py
```
If you have 2FA enabled, you will need to generate an app-specific password from your mail account.

## ⭐️ Features
* Block emails
* Reply to blocked emails with fancy HTML (or delete the HTML file to only send plain text)
* Archive blocked messages to a plain text file locally
* Handles internet connection issues
* Work with any IMAP/SMTP mail account. 
* Easy to use and customize

Run `python3 setup_wizzard.py` if you want to configure the bot without running it right away.

Or you can edit `config files/config.yml` directly while the program is running.

## ⚠️ Note!
Blacklisted emails will _PERMANENTLY DELETE_ from your mail account by default, like a spam filter. It skips the trash.
Do not blacklist email addresses you don't want gone forever! 

Plain text archives are saved by default, but you can change that in the config.
