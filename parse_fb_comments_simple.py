#!/usr/local/bin/python3.3

import urllib
import urllib.request
import urllib.parse
from urllib.parse import urlparse
import json
import feedparser

user_id = '582270449' # public Facebook uID; default is Max Woolf's

feed = feedparser.parse("http://feeds.feedburner.com/TechCrunch/")

items = feed["items"]
num_rss = len(items)



# Convert RSS feed entries into Python dicts

item_list = [dict() for x in range(num_rss)]

for i in range(num_rss):
    entry = items[i]
    item_list[i] = {'title': entry["title"],'url': entry["feedburner_origlink"],'author': entry["author_detail"]["name"], 'date': entry["published"]}



# Get Comment Thread IDs for each entry (needed to associate entry with comment)

fb_query_urls = ""

for item in item_list:
    fb_query_urls += ("\'" + item['url'] + "\',")

query_string = 'https://graph.facebook.com/fql?q=' + urllib.parse.quote_plus('SELECT comments_fbid FROM link_stat WHERE url IN (%s)' % fb_query_urls[:-1])

response = urllib.request.urlopen(query_string)

data = json.loads(response.read().decode('utf8'))['data']

for i in range(num_rss):
    item_list[i]['comments_fbid'] = str(data[i]['comments_fbid'])




### Get Top-Level Comments for each Entry from specified Facebook uID

query_string = 'https://graph.facebook.com/fql?q=' + urllib.parse.quote_plus('SELECT post_fbid, id, text, time, likes, comment_count FROM comment WHERE object_id IN (SELECT comments_fbid FROM link_stat WHERE url IN (%s)) AND fromid = \'%s\' AND parent_id = \'0\'' % (fb_query_urls[:-1],user_id))

response = urllib.request.urlopen(query_string)

data = json.loads(response.read().decode('utf8'))['data']

comment_list = [dict() for x in range(len(data))]

for i in range(len(comment_list)):
    comment_list[i] = dict(data[i])
    comment_list[i]['comments_fbid'] = data[i]['id'].split('_')[0] # thread ID


# Merge Entry dicts and Comment dicts

merged_list = []

for comment in comment_list:
    for item in item_list:
        if(comment['comments_fbid']==item['comments_fbid']): merged_list.append(dict(comment, **item)) # not efficient, but still effective

### Print the final output

print("Comments On the Last %s Articles\n" % num_rss)

for comment in merged_list:
    print('Article: %s by %s' % (comment['title'],comment['author']) )
    print('Comment: %s' % comment['text'])
    print('Likes: %s ' % comment['likes'])
    print('Replies: %s \n' % comment['comment_count'])


