#!/usr/bin/env python

from api.streaming import TwitterStream_v_1_1
import simplejson as json

oauth_keys = json.load(open('oauth.json', 'r'))

t = TwitterStream_v_1_1(**oauth_keys)
for tweet in t.iter_tweets():
    if 'text' in tweet and 'user' in tweet and 'created_at' in tweet:
        print "@%s: %s [%s]" % (tweet['user']['screen_name'], tweet['text'], tweet['created_at'])

"""
{
'contributors': None,
'truncated': False,
'text': 'AMD FX-8350 Vishera 4.0GHz (4.2GHz Turbo) AM3+ 125W Eight-Core CPU for $169.99 w/ Free FarCry3 &amp; Free Shipping at http://t.co/AKf1oIRTlj!',
'in_reply_to_status_id': None,
'id': 408004007949398018,
'favorite_count': 0,
'source': '<a href="https://about.twitter.com/products/tweetdeck" rel="nofollow">TweetDeck</a>',
'retweeted': False,
'coordinates': None,
'entities': {
    'symbols': [],
    'user_mentions': [],
    'hashtags': [],
    'urls': [
        {
            'url': 'http://t.co/AKf1oIRTlj',
            'indices': [118, 140],
            'expanded_url': 'http://bit.ly/1eTPLEg',
            'display_url': 'bit.ly/1eTPLEg'
        }
    ]
},
'in_reply_to_screen_name': None,
'id_str': '408004007949398018',
'retweet_count': 0,
'in_reply_to_user_id': None,
'favorited': False,
'user': {
    'follow_request_sent': None,
    'profile_use_background_image': True,
    'default_profile_image': False,
    'id': 46443549,
    'verified': True,
    'profile_image_url_https': 'https://pbs.twimg.com/profile_images/258925410/shell_shocker_normal.png',
    'profile_sidebar_fill_color': 'F7BB3F',
    'profile_text_color': '444444',
    'followers_count': 73982,
    'profile_sidebar_border_color': 'FFA200',
    'id_str': '46443549',
    'profile_background_color': '000000',
    'listed_count': 3381,
    'profile_background_image_url_https': 'https://si0.twimg.com/profile_background_images/591762816/x3y5pz5329e6lif1jrng.jpeg',
    'utc_offset': -28800,
    'statuses_count': 2719,
    'description': 'Official http://Newegg.com deal stream! Get the best computer & consumer electronics deals! Follow @Newegg for the latest news & announcements.',
    'friends_count': 889,
    'location': 'Southern California',
    'profile_link_color': '0084B4',
    'profile_image_url': 'http://pbs.twimg.com/profile_images/258925410/shell_shocker_normal.png',
    'following': None,
    'geo_enabled': False,
    'profile_banner_url': 'https://pbs.twimg.com/profile_banners/46443549/1386032558',
    'profile_background_image_url': 'http://a0.twimg.com/profile_background_images/591762816/x3y5pz5329e6lif1jrng.jpeg',
    'name': 'Newegg.com Deals',
    'lang': 'en',
    'profile_background_tile': False,
    'favourites_count': 6,
    'screen_name': 'NeweggHotDeals',
    'notifications': None,
    'url': 'http://Newegg.com',
    'created_at': 'Thu Jun 11 17:49:43 +0000 2009',
    'contributors_enabled': False,
    'time_zone': 'Pacific Time (US & Canada)',
    'protected': False,
    'default_profile': False,
    'is_translator': False
},
'geo': None,
'in_reply_to_user_id_str': None,
'possibly_sensitive': False,
'lang': 'en',
'created_at': 'Tue Dec 03 22:45:10 +0000 2013',
'filter_level': 'medium',
'in_reply_to_status_id_str': None,
'place': None
}
"""
