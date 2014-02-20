import simplejson as json
import urllib
#import oauth2 as oauth
import eventlet
oauth = eventlet.import_patched('oauth2')
import time

class Twitter_v_1_1:
    def __init__(self, consumer_key, consumer_secret, user_key, user_secret):
        consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)
        token = oauth.Token(key=user_key, secret=user_secret)
        self.client = oauth.Client(consumer, token)
    
    def request(self, url, method="GET", parameters=[], headers=None, body=''):
        if isinstance(parameters, dict):
            parameters = parameters.items()
        method = method.upper()
        if method == "POST"  and not body and parameters:
            body = urllib.urlencode(parameters)
        elif method == "GET" and parameters:
            url = url + '?' + urllib.urlencode(parameters)
        
        resp = None
        content = None
        clock = 0
        while content == None or (clock < 60 and resp.status >= 500):
            resp, content = self.client.request(url, method=method, body=body, headers=headers)
            if resp.status == 500:
                clock += 10
                time.sleep(10)
            elif resp.status == 502 or resp.status == 503:
                clock += 5
                time.sleep(5)
            #print resp.status, clock
        return resp, content
    
    ######
    # The good stuff
    ######
    def get_home_timeline(self, **kwargs):
        url = "https://api.twitter.com/1.1/statuses/home_timeline.json"
        r, c = self.request(url, parameters=kwargs)
        if r.status != 200:
            print r.status
            return []
        return json.loads(c)
    
    def send_tweet(self, **kwargs):
        url = "https://api.twitter.com/1.1/statuses/update.json"
        r, c = self.request(url, method="POST", parameters=kwargs)
        if r.status != 200:
            print r.status
            return None
        return json.loads(c)


Twitter = Twitter_v_1_1
