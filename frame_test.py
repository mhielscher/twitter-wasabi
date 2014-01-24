import codecs
import simplejson as json
from api.streaming import TwitterStream_v_1_1
from gui.webkit.frame import Frame
import eventlet


oauth_keys = json.load(open('oauth.json', 'r'))

gthread = eventlet.spawn(t.iter_tweets())
t = TwitterStream_v_1_1(**oauth_keys)
f = Frame(t.iter_tweets())
