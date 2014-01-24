#!/usr/bin/python

from jinja2 import Template
import os

#template_dir = os.path.dirname(os.getcwd()+'/'+__file__)+'/templates'
template_dir = os.path.dirname(__file__)+'/templates'
print template_dir

class Tweet:
    def __init__(self, tweet):
        self.data = tweet
        if self.validate():
            self.template = Template(open(template_dir+'/tweet.html', 'r').read())
            self.html = self.template.render(tweet=self.data)
    
    def validate(self):
        return ('text' in self.data and 'user' in self.data and 'created_at' in self.data)

