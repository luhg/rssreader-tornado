
import re
import feedparser
from time import mktime
from datetime import datetime

import MySQLdb

import pprint
import time


import threading
import Queue
import urllib2
import time

import hashlib




class AddFeedContentThread(threading.Thread):
    
    def __init__(self, queue):
        
        threading.Thread.__init__(self)
        self.queue = queue
        
        self.db = MySQLdb.connect(
                        host = 'localhost', 
                        user = 'xxx', 
                        passwd= "xxx", 
                        db = 'rss_db',
                        use_unicode=True, 
                        charset="utf8")
        return
    
    def run(self):
        
        while True:
            feed = self.queue.get()
            #print feed
            query_content_stmt = """SELECT `content_id`,'content_update' FROM  `rss_feed_contents` WHERE `content_link` = '%s'"""
            cur = self.db.cursor()
        
            command = cur.execute(query_content_stmt %(feed['link']))
            print command
            if cur.rowcount == 1:
                reslut = cur.fetchone()
                if(reslut[1] != feed['update']):
                
                    try:
                        update_stmt = """UPDATE `rss_feed_contents` SET `content_title`  = '%s', `content_summary` = '%s', `content_update` = '%s'"""
                        cur.execute(update_stmt %(feed['title'], feed['summary'], feed['update']))
                        self.db.commit()
                    except MySQLdb.Error, e:
                    
                        self.db.rollback()
                        print "Raise error : %s" %(e)
        
            else:
            
                try:
                    insert_content_stmt = """INSERT INTO  `rss_feed_contents`  VALUES(NULL, %d, '%s', '%s', '%s', '%s', %d)"""
            
                    cur.execute(insert_content_stmt %(feed['feed_id'], feed['title'], \
                                                      feed['link'], feed['summary'], feed['update'], int(time.time())))
                    self.db.commit()
                    
                    
                    
                except MySQLdb.Error, e:
                    self.db.rollback()
                    print "raise error : %s" %( e)
                    
            self.queue.task_done()
            


#pprint.pprint (d)



class FeedsManager:
    
    def __init__(self):
        
        self.db = MySQLdb.connect(
                        host = 'localhost', 
                        user = 'root', 
                        passwd= "thomas", 
                        db = 'rss_db',
                        use_unicode=True, 
                        charset="utf8")
        
        self.feedscur = self.db.cursor()
        
        self.queue = Queue.Queue()
                    
    
    def makeFeed(self):
        self._on_fetch_feeds()
        
    def _on_fetch_feeds(self):
        feed_stmt = """SELECT `feed_id`, `feed_url` FROM `rss_feeds`"""
        
        self.feedscur.execute(feed_stmt)
        
        
        rowcount = int(self.feedscur.rowcount)
        
        num = rowcount / 5
        
        for i in range(0, num + 1):
            results = self.feedscur.fetchmany(5)
           # print "%d item(s) :" %(i)
            for result in results:
                self._BuildFeed(*result)

                
        return
    
    
    def _BuildFeed(self, feed_id, url):
    
        
        d = feedparser.parse(url)
        feed = dict()
        feed['feed_id'] = feed_id
    
        for e   in  d.entries:
            if "content" in e:
                feed['summary'] = e.content[0]["value"]
            elif 'description' in e:
                feed['summary'] = e.description
            else:
                feed['summary'] = e.summary
                
            feed['link'] = e.link
            feed['title'] = e.title

       
            feed['content_md5'] = 
            #print feed
            self.queue.put(feed)
                
        
    def insertNewFeedContent(self,feed_id, title, link, summary, update):
        query_content_stmt = """SELECT `content_id`,'content_update' FROM  `rss_feed_contents` WHERE link = '%s'"""
        cur = self.db.cursor()
        
        command = cur.execute(query_content_stmt %(link))
        
        if cur.rowcount() == 1:
            reslut = cur.fetchone()
            if(reslut[1] != update):
                
                try:
                    update_stmt = """UPDATE `rss_feed_contents` SET `title`  = '%s', `summary` = '%s', `update` = '%s'"""
                    cur.execute(update_stmt %(title, summary, update))
                    self.db.commit()
                except MySQLdb.Error, e:
                    
                    self.db.rollback()
                    print "Raise error : %s" %(e)
        
        else:
            
            try:
                insert_content_stmt = """INSERT INTO  `rss_feed_contents`  VALUES(NULL, %d, '%s', '%s', '%s', %s, %d)"""
            
                cur.execute(insert_content_stmt %(feed_id, title, link, summary, update, int(time.time())))
                self.db.commit()
            except MySQLdb.Error, e:
                self.db.rollback()
                print "raise error : %s" %( e)
        
            
            
    

def insertNewFeedContent(self,feed_id, title, link, summary, update):
        query_content_stmt = """SELECT `content_id`,'content_update' FROM  `rss_feed_contents` WHERE link = '%s'"""
        cur = self.db.cursor()
        
        command = cur.execute(query_content_stmt %(link))
        
        if cur.rowcount() == 1:
            reslut = cur.fetchone()
            if(reslut[1] != update):
                
                try:
                    update_stmt = """UPDATE `rss_feed_contents` SET `title`  = '%s', `summary` = '%s', `update` = '%s'"""
                    cur.execute(update_stmt %(title, summary, update))
                    self.db.commit()
                except MySQLdb.Error, e:
                    
                    self.db.rollback()
                    print "Raise error : %s" %(e)
        
        else:
            
            try:
                insert_content_stmt = """INSERT INTO  `rss_feed_contents`  VALUES(NULL, %d, '%s', '%s', '%s', %s, %d)"""
            
                cur.execute(insert_content_stmt %(feed_id, title, link, summary, update, int(time.time())))
                self.db.commit()
            except MySQLdb.Error, e:
                self.db.rollback()
                print "raise error : %s" %( e)
        
        
def fetchFeeds(cur):
    
    query_stmt = """SELECT `feed_id`, `feed_url` FROM `rss_feeds`"""
    try:
        command = cur.execute(query_stmt)
        
        numtakes = int(cur.rowcount) / 5
        
        for x in range(0, numtakes + 1):
            print " %d time(s) fetch :" %(x)
            results =  cur.fetchmany(5)
            
            for row in results:
                print row
            
        
            
    except MySQLdb.Error, e:
        print "Fetch  error: ", e


def insertNewFeed(feed_id, url):
    
    feed_url = "http://www.ppurl.com/feed"
    d = feedparser.parse(feed_url)
    feed = dict()
    feed['feed_id'] = feed_id
    
    for e   in  d.entries:
        if "content" in e:
            feed['summary'] = e.content[0]["value"]
        elif 'description' in e:
            feed['summary'] = e.description
        else:
            feed['summary'] = e.summary
            feed['link'] = e.link
            feed['title'] = e.title

       
        if 'updated_parsed' in e:
            feed['update'] = e.updated_parsed
            #print "st:",mktime(st)
            feed['update'] = str(mktime(update))
            feed['update'] +=  e.updated
            #print "updated: ", st 
        else:
            fed['update'] = e.updated
            dt = int(time.time())
            feed['update'] = str(dt)  + update
        
        
        
def worker(feeds_manager):
    feeds_manager.makeFeed()

if __name__ == "__main__":
    
    fm = FeedsManager()
    t = threading.Thread(target=worker, args=(fm,))
    t.start()
    time.sleep(5)
    for i in range(5):
              t = AddFeedContentThread(fm.queue)
              t.setDaemon(True)
              t.start()
              
    
    
    fm.queue.join()
    print "over"
    



