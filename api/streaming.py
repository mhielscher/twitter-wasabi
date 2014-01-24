import simplejson as json
import time
import StringIO
import requests
from requests_oauthlib import OAuth1
import fcntl
import os
import socket

class TwitterStream_v_1_1:
    def __init__(self, consumer_key, consumer_secret, user_key, user_secret):
        self.auth = OAuth1(consumer_key, consumer_secret, user_key, user_secret)
        self.stream = requests.get('https://userstream.twitter.com/1.1/user.json', auth=self.auth, stream=True)
        fcntl.fcntl(self.stream.raw.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)
    
    def iter_tweets(self):
        buf = StringIO.StringIO()
        done = False
        while not done:
            try:
                char = self.stream.raw.read(1)
            except socket.error:
                #time.sleep(0.25)
                yield None
                continue
            buf.write(char)
            try:
                tweet = json.loads(buf.getvalue())
                buf.close()
                yield tweet
                buf = StringIO.StringIO()
            except ValueError:
                pass
    
    
