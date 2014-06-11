from twitter import *
import logging
import datetime
import os
import re

now = datetime.datetime.now()

CONSUMER_KEY = os.environ['CONSKEY']
CONSUMER_SECRET = os.environ['CONSSECRET']
OAUTH_TOKEN = os.environ['OTOKEN']
OAUTH_SECRET = os.environ['OSECRET']


logging.basicConfig(filename='/root/parrot/parrotBIN/logs/megaphone.log',
                    level=logging.INFO,
                    format='%(asctime)s: %(message)s')

# Initialize twitter
t = Twitter(
            auth=OAuth(OAUTH_TOKEN, OAUTH_SECRET,
                       CONSUMER_KEY, CONSUMER_SECRET)
           )

parrotText = t.statuses.user_timeline(screen_name="megaphonekoth")[0].get('text')

sourceStatus =  t.statuses.user_timeline(screen_name="jadekoth")[0]
sourceText = sourceStatus.get('text')

strTime = ' '.join(sourceStatus.get('created_at').split(' ')[:4]) + ' ' + str(now.year)
dtime = datetime.datetime.strptime(strTime, '%a %b %d %H:%M:%S %Y')
time_diff = now - dtime

if time_diff.seconds // 60 > 5:
	logging.info("timediff " + str(time_diff.seconds // 60))
	print "timediff " + str(time_diff.seconds // 60)
	exit(0)

logging.info("Tweeting " + sourceText)
print "Tweeting" + sourceText
t.statuses.update(status=sourceText)

count = 0
statusCount = 0

while time_diff.seconds // 60 < 5:

	logging.info("Listening for flurry. [" +
				 str(count) + " min, " + str(statusCount) + " statuses]" ) 	
	sleep(60)

	parrotText = t.statuses.user_timeline(screen_name="megaphonekoth")[0].get('text')

	sourceStatus =  t.statuses.user_timeline(screen_name="jadekoth")[0]
	sourceText = sourceStatus.get('text')
	
	r = re.compile(r"(http://[^ ]+)")

	if r.sub(r'', sourceText) != r.sub(r'', parrotText) and "vine" not in sourceText:
		logging.info("Tweeting " + sourceText)
		print "Tweeting" + sourceText
		t.statuses.update(status=sourceText)
		statusCount = statusCount + 1

	if statusCount > 6:
		logging.info("Counted over 6")
		break

	count = count + 1

	strTime = ' '.join(sourceStatus.get('created_at').split(' ')[:4]) + ' ' + str(now.year)
	dtime = datetime.datetime.strptime(strTime, '%a %b %d %H:%M:%S %Y')
	now = datetime.datetime.now()
	time_diff = now - dtime

print "Done listening"