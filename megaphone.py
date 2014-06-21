from twitter import *
import logging
import datetime
import os
import re
from time import sleep

BOT_PATH = 'KOTHPATH'
WAIT_PERIOD = 17

# Initialize logging
logfile = os.environ.get(BOT_PATH) + 'log.txt'
logging.basicConfig(filename=logfile,
                    level=logging.INFO,
                    datefmt='%H:%M:%S',
                    format='%(asctime)s: %(message)s')


class Status:
    def __init__(self, text=None, time=None):
        self.text = text
        self.time = time


def main():

    # Get acct info
    acctDict = getAcctData()

    # Initialize twitter
    try:
        t = Twitter(
            auth=OAuth(acctDict['OTOKEN'], acctDict['OSECRET'],
                       acctDict['CONSKEY'], acctDict['CONSSECRET'])
        )
    except Exception as e:
        logging.info('ERR: ' + str(e))

    startTime = initTime()

    statuses = grabStatuses(t, acctDict['SN'])
    tweetCount = 0

    # Start from source's 10th oldest tweet and move to newest
    # Script runs every 3min, so this can handle ~1tweet/18s
    for tweet in reversed(statuses[0:10]):
        status = Status()
        status.text = tweet.get('text')
        status.time = parseTime(tweet, startTime)
        age = startTime - status.time

        if(age.seconds < 180 + (tweetCount * WAIT_PERIOD)):
            # Remove mention so that we're not annoyting (yet)
            status.text = str(re.sub('@', '', status.text))
            status.text = status.text + " #DeadFly"
            logAndTweet(t, status, age)
            tweetCount = tweetCount + 1

    if tweetCount > 0:
        logging.info("Tweeted %d times" % tweetCount)
    else:
        logging.info('age=' + str(age.seconds) + "s SKIP: " + status.text)


def getAcctData():
    # Get Oauth info from file
    keyfile = os.environ.get(BOT_PATH) + 'keyfile.txt'
    Odict = {}
    lines = [line.strip() for line in open(keyfile)]
    for line in lines:
        key, value = tuple(line.split('='))
        Odict[key] = value
        print "%s: %s" % (key, value)
    return Odict


def initTime():
    # Initialize time
    startTime = datetime.datetime.now()

    # If it's a new day, put day header in logs
    if int(startTime.strftime('%H0%M')) < 3:
        logging.info(startTime.strftime('---   %b %d   ---'))
    return startTime


def grabStatuses(t, sn):
    # Grab statuses
    try:
        statuses = t.statuses.user_timeline(screen_name=sn)
    except Exception as e:
        logging.info('ERR: ' + str(e))

    return statuses


def parseTime(status, startTime):
    # Take status and return datetime object
    strTime = ' '.join(
        status.get('created_at').split(' ')[:4]) + ' ' + str(startTime.year)
    return datetime.datetime.strptime(strTime, '%a %b %d %H:%M:%S %Y')


def youngEnough(time, startTime):
    # Measure Tweet's age
    tweet_age = startTime - time
    return tweet_age.seconds < 180 and startTime.day == time.day


def logAndTweet(t, status, age):
    logging.info('Source time was: %s' % str(status.time))
    logging.info("age=%3ss POST: \'%s\'" %
                 (str(age.seconds), status.text))
    try:
        t.statuses.update(status=status.text)
    except Exception as e:
        logging.info('ERR: ' + str(e))
    sleep(WAIT_PERIOD)
    print status.text

if __name__ == '__main__':
    main()
