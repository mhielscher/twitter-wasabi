#!/usr/bin/env python

from api.rest import Twitter
import simplejson as json

oauth_keys = json.load(open('oauth.json', 'r'))

t = Twitter(**oauth_keys)
tweets = t.get_home_timeline(count=10)

for tweet in tweets:
	print "@"+tweet['user']['screen_name']
	print "  "+tweet['text']
	print ''
