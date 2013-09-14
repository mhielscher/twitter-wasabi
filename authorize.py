import urlparse
import oauth2 as oauth
import BaseHTTPServer
import webbrowser
import simplejson as json

consumer_key = 'YdG3pB7U6Z08JzSEvekbA'
consumer_secret = 'azbSWBVtjRMfl4PsVc0thQZTHJHeDOuyFNR9t5OgQ'

request_token_url = 'https://api.twitter.com/oauth/request_token'
access_token_url = 'https://api.twitter.com/oauth/access_token'
authorize_url = 'https://api.twitter.com/oauth/authorize'

consumer = oauth.Consumer(consumer_key, consumer_secret)
client = oauth.Client(consumer)

# Step 1: Get a request token. This is a temporary token that is used for 
# having the user authorize an access token and to sign the request to obtain 
# said access token.

resp, content = client.request(request_token_url, "GET")
if resp['status'] != '200':
    raise Exception("Invalid response %s." % resp['status'])

request_token = dict(urlparse.parse_qsl(content))
print request_token

print "Request Token:"
print "    - oauth_token        = %s" % request_token['oauth_token']
print "    - oauth_token_secret = %s" % request_token['oauth_token_secret']
print 

# Step 2: Redirect to the provider. Since this is a CLI script we do not 
# redirect. In a web application you would redirect the user to the URL
# below.

#print "Go to the following link in your browser:"
#print "%s?oauth_token=%s" % (authorize_url, request_token['oauth_token'])
#print 
webbrowser.open_new_tab("%s?oauth_token=%s" % (authorize_url, request_token['oauth_token']))
oauth_verifier = None

# Step 3: Once the consumer has redirected the user back to the oauth_callback
# URL you can request the access token the user has approved. You use the 
# request token to sign this request. After this is done you throw away the
# request token and use the access token returned. You should store this 
# access token somewhere safe, like a database, for future use.

# Step 3: Once the consumer has approved the app, receive the callback,
# process the URL parameters, check the token returned, and save the
# verifier.

# Set up a very simple local HTTP server to receive the callback.
class CallbackHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        global oauth_verifier, request_token
        parsed = urlparse.urlparse(self.path)
        params = dict(urlparse.parse_qsl(parsed.query))
        if params['oauth_token'] != request_token['oauth_token']:
            response = """<html>
<head>
<title>Token Mismatch</title>
</head>
<body>
<h1>OAuth Token Mismatch</h1>
<p>OAuth token returned did not match OAuth token sent. Try again in a minute?</p>
</body>
</html>
"""
            self.wfile.write("HTTP/1.1 401 Not Authorized\r\n")
            self.wfile.write("Content-type: text/html\r\n")
            self.wfile.write("Content-length: %d\r\n" % len(response))
            self.wfile.write("\r\n")
            self.wfile.write(response)
        
        else:
            oauth_verifier = params['oauth_verifier']
            response = """<html>
<head>
<title>OAuth Approved</title>
</head>
<body>
<h1>Approved</h1>
<p>You have authorized this app successfully. The script is now saving your OAuth user tokens. You may close this window.</p>
</body>
</html>
"""
            self.wfile.write("HTTP/1.1 200 Success\r\n")
            self.wfile.write("Content-type: text/html\r\n")
            self.wfile.write("Content-length: %d\r\n" % len(response))
            self.wfile.write("\r\n")
            self.wfile.write(response)

CallbackHTTPRequestHandler.protocol_version = "HTTP/1.1"
httpd = BaseHTTPServer.HTTPServer(('127.0.0.1', 4212), CallbackHTTPRequestHandler)

sa = httpd.socket.getsockname()
print "Waiting for callback on", sa[0], "port", sa[1], "..."
httpd.handle_request()

token = oauth.Token(request_token['oauth_token'],
    request_token['oauth_token_secret'])
token.set_verifier(oauth_verifier)
print token
client = oauth.Client(consumer, token)

resp, content = client.request(access_token_url, "POST")
access_token = dict(urlparse.parse_qsl(content))
#print access_token

oauth_data = {"consumer_key": consumer_key,
            "consumer_secret": consumer_secret,
            "user_key": access_token['oauth_token'],
            "user_secret": access_token['oauth_token_secret']}
json.dump(oauth_data, open('oauth.json', 'w'))

print "Access Token:"
print "    - oauth_token        = %s" % access_token['oauth_token']
print "    - oauth_token_secret = %s" % access_token['oauth_token_secret']
print
print "You may now access protected resources using the access tokens above." 
print "They have also been written to oauth.json."
print

