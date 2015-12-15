import praw
from OAuth2Util import OAuth2Util
from time import sleep
import ConfigParser
import datetime
import pytz
import smtplib
from email.mime.text import MIMEText


configFile = "bbbot.ini"
config = ConfigParser.ConfigParser()
config.read(configFile)
subreddit = config.get('config', 'subreddit')
r = praw.Reddit("New application for /r/bodybuilding by /u/timlardner - v2.0 alpha")
o = OAuth2Util(r)
o.refresh()


def tryPost(postType):
    attempt_start = datetime.datetime.now()
    success = False
    while (datetime.datetime.now()-attempt_start) < datetime.timedelta(hours=2):
        try:
            if postType == 'discussion':
                makeDiscussionPost()
            elif postType == 'topical':
                makeTopicalPost()
            success = True
            break
        except:
            print("Failed to make daily post. Waiting 15 minutes to retry")
            sleep(15*60) #Sleep in seconds
    if not success:
        # Email failure status
        reportFailure(postType)

def reportFailure(failedPost):
    if failedPost == 'topical':
        subject = "Today's topical post has failed"
    elif failedPost == 'discussion':
        subject = "Today's daily discussion post has failed"
    else:
        subject = failedPost
    email_list = []
    config_list = config.items('config')
    for items in config_list:
        if "fail_email" in items[0]:
            email_list.append(items[1])
    print email_list
    try:
        emailConfigFile = 'smtp.ini'
        emailConfig = ConfigParser.ConfigParser()
        emailConfig.read(emailConfigFile)
    except:
        print("No email account configured, cannot send email.")
    sender = emailConfig.get('smtp','username')
    password = emailConfig.get('smtp','password')
    server = emailConfig.get('smtp','server')
    recipients = email_list
    msg = MIMEText("""The reddit post named in the subject of this email has failed.""")
    msg['Subject'] = subject
    msg['From'] = "Bodybuilding Bot <"+sender+">"
    msg['To'] = ", ".join(recipients)
    smtpserver = smtplib.SMTP_SSL(server, 465)
    smtpserver.login(sender,password)
    smtpserver.sendmail(sender, recipients, msg.as_string())
    smtpserver.close()

def makeDiscussionPost():
    if not shouldDiscussionPost():
        print "Daily post already made"
        return
    title = config.get('daily','title')
    body = config.get('daily','body')
    submission = r.submit(subreddit,datetime.datetime.strftime(datetime.datetime.now(pytz.timezone('US/Eastern')), title),text=body).sticky()

def makeTopicalPost():
    # Get the topical post from the config file
    week   = ['Monday',
              'Tuesday',
              'Wednesday',
              'Thursday',
              'Friday',
              'Saturday',
              'Sunday']
    weekday = week[datetime.datetime.today().weekday()]
    title_list,body_list = getPostContent(str.lower(weekday))
    if not title_list:
        return
    for i in range(len(title_list)):
        title = title_list[i]
        body = body_list[i]
        # Check to see if we should be submitting this post today. This is important to do here, in case one post
        # is submitted and another fails. We don't want to repost both of them
        if not shouldTopicalPost(title):
            print("We've already posted "+title+ " recently.")
            return
        submission = r.submit(subreddit,title,text=body)

def getPostContent(weekday):
    day_list = config.items(weekday)
    title_list = []
    body_list = []
    if not day_list[0][1]:
        return None,None
    else:
        for entries in day_list:
            if 'title' in entries[0]:
                title_list.append(entries[1])
            elif 'body' in entries[0]:
                body_list.append(entries[1])
            else:
                raise Exception('Unexpected field in config')
    if len(title_list)!=len(body_list):
        raise Exception('More post titles than bodies. Configuration problem')
    return title_list,body_list

def shouldDiscussionPost():
    username = config.get('config','bot_username')
    user = r.get_redditor(username)
    now = datetime.datetime.now()
    shouldPost = True
    for submission in user.get_submitted(limit=14):
        post_time = datetime.datetime.fromtimestamp(int(submission.created_utc))
        time_delta = now - post_time
        # We'll run this every hour. Since it takes a few seconds to process and make the post, we'll relax the
        # time requirement to every 22.5 hours. This means that on the hour it's supposed to post, it can.
        if 'Daily Discussion Thread' in submission.title and time_delta < datetime.timedelta(hours=22.5):
            shouldPost = False
    return shouldPost

def shouldTopicalPost(title):
    username = config.get('config','bot_username')
    user = r.get_redditor(username)
    now = datetime.datetime.now()
    shouldPost = True
    for submission in user.get_submitted(limit=14):
        post_time = datetime.datetime.fromtimestamp(int(submission.created_utc))
        time_delta = now - post_time
        # We only want to post each of these once a week. We'll settle for ensuring one of these threads hasn't been
        # posted in the last 5 days. Just in case.
        if title in submission.title and time_delta < datetime.timedelta(days=5):
            shouldPost = False
    return shouldPost