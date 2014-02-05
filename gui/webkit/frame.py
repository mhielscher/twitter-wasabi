from gi.repository import Gtk, Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import WebKit
#from gi.repository import Soup
import sys
import webbrowser
import urlparse
import requests
import time
import os
import tweet
import threading
import Queue
import time

class Frame:
    webkit_settings = [
        ('enable-default-context-menu', True),
        ('enable-java-applet', False),
        ('enable-plugins', False),
        ('enable-page-cache', False),
        ('enable-offline-web-application-cache', False),
        ('enable-html5-local-storage', False),
        ('enable-html5-database', False),
        ('enable-xss-auditor', True),
        ('enable-dns-prefetching', True),
        ('resizable-text-areas', True)
    ]
    
    def __init__(self, tweet_source, rest_api):
        # Default window size
        self.default_width = 340
        self.default_height = 700
        
        # Minimum window size
        self.min_width = 200
        self.min_height = 400
        
        # Non-mobile photo workaround
        self.photo_workaround = True
        
        self.config_dir_path = '.'
        self.config_path = os.path.join(self.config_dir_path, "twitter.conf")
        self.config_save_interval = 120
        self.refresh_time = 5
        
        self.last_save = time.time()
        self.window_geometry = {'x': 0, 'y': 0, 'w': self.default_width, 'h': self.default_height}
        self.save_scheduled = False
        self.refresh_count = 0
        
        self.tweet_source = tweet_source.iter_tweets()
        self.tweet_queue = Queue.Queue()
        self.tweets = {}
        self.to_delete = []
        
        self.rest = rest_api
        preloaded_tweets = self.rest.get_home_timeline(count=50)
        for twt in preloaded_tweets:
            self.tweets[twt['id']] = tweet.Tweet(twt)
        
        GObject.threads_init()
        
        self.tweet_thread = threading.Thread(target=self.retrieve_tweets)
        self.tweet_thread.daemon = True
        self.tweet_thread.start()
        
        self.update_content()
        self.init_view()
        
    def init_view(self):
        settings = WebKit.WebSettings()
        for setting in self.webkit_settings:
            settings.set_property(*setting)
        
        dimensions = self.load_config()
        
        self.view = WebKit.WebView()
        self.view.set_settings(settings)
        
        self.sw = Gtk.ScrolledWindow()
        self.sw.add(self.view)

        self.win = Gtk.Window()
        self.win.set_size_request(self.min_width, self.min_height)
        self.win.resize(dimensions['w'], dimensions['h'])
        self.win.move(dimensions['x'], dimensions['y'])
        self.win.add(self.sw)
        self.win.set_title("Wasabi Twitter")
        self.win.connect("destroy", Gtk.main_quit)
        self.win.connect("configure-event", self.window_resized)
        self.win.show_all()

        #self.view.connect("navigation-requested", self.on_nav_req)
        self.view.connect("new-window-policy-decision-requested", self.open_external_link)
        self.view.connect("navigation-requested", self.open_link)
        GLib.timeout_add_seconds(self.refresh_time, self.fetch_tweets, self.view, self.sw)
        
        self.view.load_string(self.full_content, "text/html", "UTF-8", "/")
        
        Gtk.main()
    
    def retrieve_tweets(self):
        for tweet in self.tweet_source:
            self.tweet_queue.put(tweet, False)
            print "Added tweet to queue."
    
    def update_content(self):
        self.top_template = open(tweet.template_dir+'/timeline-top.html', 'r').read()
        self.content = ""
        for tid, twt in sorted(self.tweets.items(), reverse=True):
            self.content += twt.render()
        self.bottom_template = open(tweet.template_dir+'/timeline-bottom.html', 'r').read()
        self.full_content = self.top_template + self.content + self.bottom_template
    
    def get_active_window(root=None):
        """Returns the active (focused, top) window, or None."""
        root = root or Gdk.get_root_window()
        # Make sure active window hinting is working
        if root.supports_net_wm_hint("_NET_ACTIVE_WINDOW") and root.supports_net_wm_hint("_NET_WM_WINDOW_TYPE"):
            active = root.get_active_window()
            # If active window is a desktop, fail
            if active.property_get("_NET_WM_WINDOW_TYPE")[-1][0] == '_NET_WM_WINDOW_TYPE_DESKTOP':
                return None
            return active
        else:
            return None
    
    def get_active_monitor(self, root=None):
        """Returns the index of the active monitor, or -1 if undetermined."""
        root = root or Gdk.get_root_window()
        num_monitors = root.get_n_monitors()
        if (num_monitors == 1):
            return 0
        active = get_active_window()
        if active != None:
            return root.get_monitor_at_window(active)
        else:
            return -1
    
    def window_resized(self, win, event, data=None):
        if event.type == Gdk.EventType.CONFIGURE:
            self.window_geometry['x'] = event.x
            self.window_geometry['y'] = event.y
            self.window_geometry['w'] = event.width
            self.window_geometry['h'] = event.height
            seconds_until_save = int(self.last_save + self.config_save_interval - time.time())
            if not self.save_scheduled:
                #print "Scheduling save for %d" % seconds_until_save
                if seconds_until_save > 0:
                    GLib.timeout_add_seconds(seconds_until_save, self.save_config)
                    self.save_scheduled = True
                else:
                    self.save_config()
        return False

    def save_config(self):
        #print "Saving new dimensions:", window_geometry
        config_file = open(self.config_path, 'w')
        print >>config_file, "x: %d" % self.window_geometry['x']
        print >>config_file, "y: %d" % (self.window_geometry['y']-32)
        print >>config_file, "w: %d" % self.window_geometry['w']
        print >>config_file, "h: %d" % self.window_geometry['h']
        config_file.close()
        self.last_save = time.time()
        self.save_scheduled = False
        return False

    def load_config(self):
        if os.path.exists(self.config_path):
            config_file = open(self.config_path, 'r')
            config = config_file.read().strip()
            dimensions = dict(line.split(': ') for line in config.split('\n'))
            for key, value in dimensions.items():
                dimensions[key] = int(value)
            return dimensions
        else:
            dimensions = {'w': self.default_width, 'h': self.default_height}
            # Get the upper-right corner of the active monitor
            root = Gdk.Screen.get_default()
            root_win = root.get_root_window()
            cursor = root_win.get_pointer()
            monitor = root.get_monitor_at_point(*cursor[1:3])
            m_rect = root.get_monitor_geometry(monitor)
            dimensions['x'] = m_rect.x + m_rect.width - self.default_width
            dimensions['y'] = m_rect.y
            return dimensions
    
    
    def on_nav_req(self, view, frame, req, data=None):
        print "Nav to %s" % req.get_uri()
        #end_url = resolve_http_redirect(req.get_uri())
        #if 'photo' in end_url and 'twitter.com' in end_url:
        if 't.co' in req.get_uri() or ('twitter.com' in req.get_uri() and 'photo' in req.get_uri() or 'pic.twitter.com' in req.get_uri()):
            #req.set_uri(end_url)
            return self.open_external_link(view, frame, req, None, None, data)
        return False
    
    def open_link(self, view, frame, req, data=None):
        print "Opening %s" % req.get_uri()
        if req.get_uri() == "/compose/tweet":
            self.full_content = open(tweet.template_dir+'/compose.html', 'r').read()
            self.view.load_string(self.full_content, "text/html", "UTF-8", "/")
            return False
        elif req.get_uri() == "/":
            return False
        else:
            return self.open_external_link(view, frame, req, None, None)
    
    def open_external_link(self, view, frame, req, nav_action, decision, data=None):
        print "Externally open %s" % req.get_uri()
        if self.photo_workaround and 'mobile.twitter.com' in req.get_uri() and 'photo' in req.get_uri():
            uri = req.get_uri().replace('mobile.', '')
            print "Workaround: %s" % uri
            webbrowser.open_new_tab(uri)
            return True
        #webbrowser.open_new_tab(resolve_http_redirect(req.get_uri()))
        webbrowser.open_new_tab(req.get_uri())
        return True
    
    def fetch_tweets(self, view, sw):
        #print self.tweets
        #print self.tweet_queue.qsize()
        while True:
            try:
                twt = self.tweet_queue.get(False)
            except Queue.Empty:
                #print "%d - No tweets." % (time.time())
                break
            print "Got tweet."
            print twt
            twt = tweet.Tweet(twt)
            if twt.validate():
                if twt.data['id'] in self.to_delete:
                    self.to_delete.remove(twt.data['id'])
                else:
                    self.tweets[twt.data['id']] = twt
                    self.update_content()
                    if view.get_uri() == "/":
                        self.view.load_string(self.full_content, "text/html", "UTF-8", "/")
            elif 'delete' in twt.data and 'status' in twt.data['delete']:
                if twt.data['delete']['status']['id'] in self.tweets:
                    self.tweets[twt.data['delete']['status']['id']].time_str = "[DEL]"
                    self.update_content()
                    if view.get_uri() == "/":
                        self.view.load_string(self.full_content, "text/html", "UTF-8", "/")
                else:
                    self.to_delete.append(twt.data['delete']['status']['id'])
        return True
    
