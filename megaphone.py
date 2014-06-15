from twitter import *
import logging
import datetime
import os
import re
from time import sleep

keyfile = os.environ['KOTHPATH'] + 'keyfile.txt'

# Get Oauth info from file
Odict = {}
lines = [line.strip() for line in open(keyfile)]
for line in lines:
	key, value = tuple(line.split('='))
	Odict[key] = value

# Initialize logging
logging.basicConfig(filename='/root/parrot/parrotBIN/log.txt',
                    level=logging.INFO,
                    datefmt='%H:%M:%S',
                    format='%(asctime)s: %(message)s')

# Initialize twitter
t = Twitter(
            auth=OAuth(Odict['OTOKEN'], Odict['OSECRET'],
                       Odict['CONSKEY'], Odict['CONSSECRET'])
           )
# Initialize time
startTime = datetime.datetime.now()

# If it's a new day, put day header in logs
if int(startTime.strftime('%H0%M')) < 3:
	logging.info(startTime.strftime('---   %b %d   ---'))

# Grab statuses
try:
	sourceStatuses =  t.statuses.user_timeline(screen_name=Odict['SN'])
except Exception as e:
	logging.info('ERR: ' + str(e))

tweetCount = 0

# Start from source's 10th oldest tweet and move to newest
# Script runs every 3min, so this can handle ~1tweet/18s
for status in reversed(sourceStatuses[0:10]):

 	# Grab text from tweet
 	sText = status.get('text')

	# Grab creation time from Twitter & remove UTC stuff that datetime doesn't like
	strTime = ' '.join(status.get('created_at').split(' ')[:4]) + ' ' + str(startTime.year)
	# Turn formatted Twitter time into date time object
	dtime = datetime.datetime.strptime(strTime, '%a %b %d %H:%M:%S %Y')
	# Measure Tweet's age
	tweet_age = startTime - dtime 	

	if tweet_age.seconds < 180 and dtime.day == startTime.day:
		# Remove mention so that we're not annoyting (yet)
		newTweet = str(re.sub('@', '', sText))
		logging.info('Source time was: %s' % str(dtime))
		logging.info("age=%3ss POST: \'%s\'" % (str(tweet_age.seconds), newTweet))
		try:
			t.statuses.update(status=newTweet)
		except Exception as e:
			logging.info('ERR: ' + str(e))
		tweetCount = tweetCount + 1
		sleep(18)
		print sText

if tweetCount > 0:
	logging.info("Tweeted %d times" % tweetCount)
else:
	logging.info('age=' + str(tweet_age.seconds) + "s SKIP: " + sText)
