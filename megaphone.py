from twitter import *
import logging
import datetime
import os
import re

now = datetime.datetime.now()

Odict = {}
# Get Oauth info from file
lines = [line.strip() for line in open('keyfile.txt')]
for line in lines:
	key, value = tuple(line.split('='))
	Odict[key] = value



logging.basicConfig(filename='/root/parrot/parrotBIN/logs/megaphone.log',
                    level=logging.INFO,
                    format='%(asctime)s: %(message)s')

# Initialize twitter
t = Twitter(
            auth=OAuth(Odict['OTOKEN'], Odict['OSECRET'],
                       Odict['CONSKEY'], Odict['CONSSECRET'])
           )
startTime = datetime.datetime.now()

sourceStatuses =  t.statuses.user_timeline(screen_name="jadekoth")

tweetCount = 0
for status in reversed(sourceStatuses[0:5]):

	strTime = ' '.join(status.get('created_at').split(' ')[:4]) + ' ' + str(startTime.year)
	dtime = datetime.datetime.strptime(strTime, '%a %b %d %H:%M:%S %Y')
	time_diff = startTime - dtime
 
 	sText = status.get('text')
	if time_diff.seconds < 180:
		newTweet = re.sub('@', '', sText)
		logging.info("Tweeting: " + newTweet)
		t.statuses.update(status=newTweet)
		tweetCount += 1
		sleep(14)

logging.info("SOURCE: (" + str(datetime) + ")" + ": " + sText)
if tweetCount > 0:
	xlogging.info("Tweeted %d times" % tweetCount)