import boto3, json, tweepy
from random import randint
import urllib
import time

def lambda_handler(event, context):

	s3 = boto3.client('s3')

	paginator = s3.get_paginator('list_objects')

	# Create a PageIterator from the Paginator
	page_iterator = paginator.paginate(Bucket='bbc-sound-bot', Prefix='todo/')

	allKeys = []

	for page in page_iterator:
	    for item in page['Contents']:
	    	key = item['Key'].split('/')
	    	if key[1] not in allKeys and len(key[1]) == 36:

	    		allKeys.append(key[1])
	    		
	    if len(allKeys) > 1000:
	    	break

	useKey = allKeys[randint(0,len(allKeys)-1)]


	try:
		s3.download_file('bbc-sound-bot', 'todo/' + useKey + '/meta.json' , '/tmp/meta.json')
		s3.download_file('bbc-sound-bot', 'todo/' + useKey + '/final.mp4' , '/tmp/final.mp4')
		with open('/tmp/meta.json') as jsondata:
			meta = json.load(jsondata)

		with open('/tmp/final.mp4') as jsondata:
			jsondata = jsondata
	except Exception as e:
		print 'Could not download image and or metadata from' + useKey
		print e.__doc__
		print e.message
		quit()



	auth = tweepy.OAuthHandler('Consumer Key (API Key)', 'Consumer Secret (API Secret)')
	auth.set_access_token('Access Token', 'Access Token Secret')
	api = tweepy.API(auth)

	msg = meta['title'] + '"\n'

	try:
		# api.update_with_media('/tmp/final.mp4', status=msg)

		upload_result = api.media_upload('/tmp/final.mp4')
		time.sleep(10)
		api.update_status(status=msg, media_ids=[upload_result.media_id_string])


	except Exception as e:
		print "Something wrong posting to twitter " + useKey
		print e.__doc__
		print e.message
		print upload_result.media_id_string
		quit()


	# remove it from s3
	s3 = boto3.resource('s3')
	bucket = s3.Bucket('bbc-sound-bot')
	for obj in bucket.objects.filter(Prefix='todo/'+useKey):
		s3.Object(bucket.name, obj.key).delete()
