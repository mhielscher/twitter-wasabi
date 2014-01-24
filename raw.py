import requests
from requests_oauthlib import OAuth1
import fcntl
import os
import simplejson as json
import StringIO
import socket

oauth_keys = json.load(open('oauth.json', 'r'))
auth = OAuth1(oauth_keys['consumer_key'], oauth_keys['consumer_secret'], oauth_keys['user_key'], oauth_keys['user_secret'])

stream = requests.get('https://userstream.twitter.com/1.1/user.json', auth=auth, stream=True, headers={'Accept-Encoding': 'identity'})
if stream.status_code != 200:
    print "Got status code %d" % (stream.status_code)
    exit(1)
fl = fcntl.fcntl(stream.raw.fileno(), fcntl.F_GETFL)
fcntl.fcntl(stream.raw.fileno(), fcntl.F_SETFL, fl | os.O_NONBLOCK)

print stream.headers
for header, value in stream.headers.items():
    print "%s: %s" % (header, value)

done = False
buf = StringIO.StringIO()
while not done:
    try:
        char = stream.raw.read(1)
        if char == '':
            print "Got empty string."
            done = True
            break
        buf.write(char)
    except socket.error:
        print "Got nonblock exception."
        print buf.getvalue()
        buf = StringIO.StringIO()
    if buf.len % 100 == 0:
        print "Read %d chars." % (buf.len)
        
"""
GET /1.1/user.json HTTP/1.1
Host: userstream.twitter.com
Authorization: OAuth oauth_nonce="101803849879202502811390599067", oauth_timestamp="1390599067", oauth_version="1.0", oauth_signature_method="HMAC-SHA1", oauth_consumer_key="YdG3pB7U6Z08JzSEvekbA", oauth_token="90100440-XTjyFrvKx9gp2wXImxMIpT4JYWUJlgTpb1bdQruhX", oauth_signature="IEil53YF1fEbA%2F5C%2BFp6Ug8tpAE%3D"
Accept-Encoding: identity
Accept: */*
User-Agent: python-requests/2.0.1 CPython/2.7.3 Linux/3.5.0-45-generic


HTTP/1.1 200 OK
transfer-encoding: chunked
date: Fri, 24 Jan 2014 21:27:00 GMT
connection: close
content-type: application/json
x-transaction: aa3fa7cb11e76c5b608af795a75a379b
"""

"""
curl -i -H 'Authorization: OAuth oauth_nonce="101803849879202502811390599067", oauth_timestamp="1390600175", oauth_version="1.0", oauth_signature_method="HMAC-SHA1", oauth_consumer_key="YdG3pB7U6Z08JzSEvekbA", oauth_token="90100440-XTjyFrvKx9gp2wXImxMIpT4JYWUJlgTpb1bdQruhX", oauth_signature="IEil53YF1fEbA/5C+Fp6Ug8tpAE="' -H 'Accept: */*' -H 'Accept-Encoding: identity' -H 'User-Agent: python-requests/2.0.1 CPython/2.7.3 Linux/3.5.0-45-generic' 'https://userstream.twitter.com/1.1/user.json'
"""
