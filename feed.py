#-*-coding:utf-8-*-

import urllib2,urllib
import re
import feedparser
from time import mktime
from datetime import datetime

import MySQLdb

import pprint

feed_url = "http://www.ppurl.com/feed"
d = feedparser.parse(feed_url)

#pprint.pprint (d)

mydb = MySQLdb.connect(
                        host = 'localhost', 
                        user = 'xxx', 
                        passwd= "xxx", 
                        db = 'rss_db',
                        use_unicode=True, 
                        charset="utf8")
                        


cur = mydb.cursor()

query_stmt = """SELECT `feed_id` FROM `rss_feeds` WHERE `feed_url` = '%s'"""
insert_statement = """INSERT INTO `rss_feeds` VALUES(NULL, '%s', '%s', NULL, NULL)"""
    

def CheckFeedVaild(feed):
    
    if 'version' in feed and feed['version'] != '':
        return True
    
    return False

if CheckFeedVaild(d):
    
    print "It's a rss url"
   
    title = d['feed']['title']
    print title
    command = cur.execute(query_stmt %(feed_url))
    if command == 0:
        command = cur.execute(insert_statement %(feed_url, title))
    else:
        print "feed url is exists"
    

else:
    print "It's not a rss url"

mydb.commit()
mydb.close()
