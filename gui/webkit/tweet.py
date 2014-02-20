#!/usr/bin/python

from jinja2 import Template
import os
import urllib
import datetime
import dateutil.parser, dateutil.tz

#template_dir = os.path.dirname(os.getcwd()+'/'+__file__)+'/templates'
template_dir = os.path.dirname(__file__)+'/templates'
print template_dir

class Tweet:
    def __init__(self, tweet):
        #print tweet
        self.data = tweet
        if 'retweeted_status' in self.data:
            retweet_wrapper = self.data.copy()
            del retweet_wrapper['retweeted_status']
            self.data = self.data['retweeted_status']
            self.data['retweet_wrapper'] = retweet_wrapper
            self.data['retweeted_by'] = retweet_wrapper['user']['screen_name']
        if self.validate():
            self.time = dateutil.parser.parse(self.data['created_at']).astimezone(dateutil.tz.tzlocal())
            if self.time.date() != datetime.datetime.today().date():
                self.time_str = self.time.strftime("%b")+self.time.strftime(" %-d %-I:%M%p").lower()
            else:
                self.time_str = self.time.strftime("%-I:%M%p").lower()
            self.template = Template(open(template_dir+'/tweet.html', 'r').read())
            self.build_html()
    
    def validate(self):
        return ('text' in self.data and 'user' in self.data and 'created_at' in self.data)
    
    def build_html(self):
        self.html = self.data['text']
        if "entities" in self.data:
            if "urls" in self.data['entities']:
                for link in self.data['entities']['urls']:
                    start_idx = link['indices'][0]
                    end_idx = link['indices'][1]
                    link_html = '<a class="twitter-timeline-link activeLink dir-ltr tco-link" target="_blank" rel="nofollow" dir="ltr" data-url="%s" href="%s">%s</a>' % (link['expanded_url'], link['url'], link['display_url'])
                    self.html = self.html.replace(self.data['text'][start_idx:end_idx], link_html)
            if "user_mentions" in self.data['entities']:
                for mention in self.data['entities']['user_mentions']:
                    start_idx = mention['indices'][0]
                    end_idx = mention['indices'][1]
                    link_html = '<a title="%s" href="https://twitter.com/%s">@%s</a>' % (mention['name'], mention['screen_name'], mention['screen_name'])
                    self.html = self.html.replace(self.data['text'][start_idx:end_idx], link_html)
            if "media" in self.data['entities']:
                for media in self.data['entities']['media']:
                    start_idx = media['indices'][0]
                    end_idx = media['indices'][1]
                    url = media['media_url']
                    if "large" in media['sizes']:
                        url += ':large'
                    link_html = '<a href="%s">%s</a>' % (url, media['display_url'])
                    self.html = self.html.replace(self.data['text'][start_idx:end_idx], link_html)
            if "hashtags" in self.data['entities']:
                for hashtag in self.data['entities']['hashtags']:
                    start_idx = hashtag['indices'][0]
                    end_idx = hashtag['indices'][1]
                    link_html = '<a href="https://twitter.com/search?q=%s&src=hash">#%s</a>' % (urllib.quote('#'+hashtag['text']), hashtag['text'])
                    self.html = self.html.replace(self.data['text'][start_idx:end_idx], link_html)
    
    def render(self):
        if self.validate():
            return self.template.render(tweet=self.data, tweet_html=self.html, tweet_time=self.time_str)
        else:
            return None

