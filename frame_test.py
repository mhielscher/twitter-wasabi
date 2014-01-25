import codecs
import simplejson as json
from api.streaming import TwitterStream_v_1_1
from gui.webkit.frame import Frame

oauth_keys = json.load(open('oauth.json', 'r'))

t = TwitterStream_v_1_1(**oauth_keys)
f = Frame(t.iter_tweets())
