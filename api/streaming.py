import simplejson as json
import urllib
import requests
from requests_oauthlib import OAuth1
import time
import StringIO

class TwitterStream_v_1_1:
    def __init__(self, consumer_key, consumer_secret, user_key, user_secret):
        self.auth = OAuth1(consumer_key, consumer_secret, user_key, user_secret)
        self.stream = requests.get('https://userstream.twitter.com/1.1/user.json', auth=self.auth, stream=True)
    
    def iter_tweets(self):
        buf = StringIO.StringIO()
        for char in self.stream.iter_content():
            buf.write(char)
            try:
                tweet = json.loads(buf.getvalue())
                buf.close()
                yield tweet
                buf = StringIO.StringIO()
            except ValueError:
                pass
    
    
