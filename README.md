# Bodybuilding Bot

New bodybuilding bot for /r/bodybuilding

This bot is designed to run as a series of cron jobs. An example cron template is shown below:

    0 5 * * * cd /home/redditbot/bbbot; python BBbot.py topical
    0 * * * * cd /home/redditbot/bbbot; python BBbot.py discussion

To use, rename `oauth.example.ini` to `oauth.ini` and populate it with your reddit API settings. In order to use the 'email on failure function', rename `smtp.example.ini` to `smtp.ini` and use your own email settings here. 