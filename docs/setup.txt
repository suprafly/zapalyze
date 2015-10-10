
# Zapalyze!

## User Guide

### About
Zapalyze! creates a visual interface for your Zapier productivity. It creates pretty charts from Daily Task Summary Emails, so that you can easily see which are performing well, and how they are performing on a daily basis.

### Requirements
* You have a gmail account
* You have your Zapier account and you have the settings set to send Daily Task Summaries to your gmail account.

### Usage
Login with the gmail account which corresponds to your Zapier account, and where you receive your Daily Task Summary reports. Zapalyze! will automatically populate a chart that tracks all of your Zaps and Tasks per day over time.

### Future Improvements
* Templates to allow any frequency of Task Summaries (weekly, monthly)
* Calendar View (daily, weekly, monthly, etc)
* Contuinity of Zaps which have their names changed
* Productivity: Allow users to describe an approximate time that each Zap saves them, then display how much time was saved per day for each Zap.

## Developer's Guide

### Setup Your Own Server
*You'll need to install a few libraries to get this working:*
* pip install django
* pip install python-social-auth
* pip install -U https://github.com/google/google-visualization-python/zipball/master

*Google Auth*
* You'll also need to [follow these instructions to setup Google Authentication|https://developers.google.com/gmail/api/quickstart/python]
 in order to get this working.



