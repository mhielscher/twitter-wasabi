#!/usr/bin/env python

import simplejson as json
import oauth2 as oauth
import urllib
import sys
from time import sleep

CONSUMER_KEY = ""
CONSUMER_SECRET = ""
USER_KEY = ""
USER_SECRET = ""

def get_oauth_keys(filename="oauth.json"):
    global CONSUMER_KEY, CONSUMER_SECRET
    global USER_KEY, USER_SECRET
    oauth_keys = json.load(open(filename, 'r'))
    CONSUMER_KEY = oauth_keys['consumer_key']
    CONSUMER_SECRET = oauth_keys['consumer_secret']
    USER_KEY = oauth_keys['oauth_token']
    USER_SECRET = oauth_keys['oauth_secret']

get_oauth_keys()

def oauth_req(url, http_method="GET", post_body='', http_headers=None, key=USER_KEY, secret=USER_SECRET):
    #print key, secret
    consumer = oauth.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)
    token = oauth.Token(key=key, secret=secret)
    client = oauth.Client(consumer, token)

    resp = None
    content = None
    clock = 0
    while content == None or (clock < 60 and resp.status >= 500):
        resp, content = client.request(url, method=http_method, body=post_body, headers=http_headers)
        if resp.status == 500:
            clock += 10
            time.sleep(10)
        elif resp.status == 502 or resp.status == 503:
            clock += 5
            time.sleep(5)
        #print resp.status, clock
    return resp, content


if __name__ == "__main__":
    url = "https://api.twitter.com/1.1/statuses/home_timeline.json"
    #head = ['Expect: ']
    data = [('include_entities', True), ('count', 50)]
    #data = [('count', 200)]
    postdata = urllib.urlencode(data)
    url = url+'?'+postdata
    print url
    r, c = oauth_req(url)
    #print r, c
    if r.status > 200:
        print "Request failed: %d" % (r.status)
        sys.exit(1)
    jdata = json.loads(c)
    #print jdata
    received = len(jdata)
    print str(received)+" tweets"
    sleep(3)
    for tweet in jdata:
        print tweet['user']['screen_name']


