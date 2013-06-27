
import threading
import feedparser
import urllib2

from tornado.escape import json_encode
import hashlib
import time

import MySQLdb


class AddFeedContentThread(threading.Thread):
    
    def __init__(self,  feed_id, url):
        
        threading.Thread.__init__(self)
      
        self.md_five = hashlib.md5()
        self.db = MySQLdb.connect(
                        host = 'localhost', 
                        user = 'xxx', 
                        passwd= "xxx", 
                        db = 'rss_db',
                        use_unicode=True, 
                        charset="utf8")
        
        self.feed_id = feed_id
        self.url = url
        self.feeds = []
        
        return
    
    def run(self):
        
        
        print "insert data : "
        
        self._update()
        
        
    
    def _update(self ):
         
        d = feedparser.parse(self.url)
        
        feed = dict()

    
        for e   in  d.entries:
            if "content" in e:
                feed['summary'] = e.content[0]["value"]
            elif 'description' in e:
                feed['summary'] = e.description
            else:
                feed['summary'] = e.summary
                
            feed['link'] = e.link
            feed['title'] = e.title
            self.md_five.update(feed['title'] + feed['summary'])
            feed['md5'] = self.md_five.hexdigest()
            exist = self._is_feed_exist_or_update(feed) 
            if( exist  == False):
                f = (self.feed_id, feed['title'], \
                                feed['link'], feed['summary'], feed['md5'], int(time.time()))
                #print "feed :", f
                self.feeds.append(f)
                
            
        
        if len(self.feeds) > 0:
            self._insert_feed_content_in_db()
#        
        
            
            
            #print feed
            
    def _is_feed_exist_or_update(self, feed):
        
     
        query_content_stmt = """SELECT `content_id`,`content_md5` FROM  `rss_feed_contents` WHERE `content_link` = '%s'"""
        cur = self.db.cursor()
        #print feed['link']
        command = cur.execute(query_content_stmt %(feed['link']))
        #print command
        if cur.rowcount == 1:
            result = cur.fetchone()
            #print result
            if(result[1] != feed['md5']):
                
                try:
                    
                    print "update %s" %(feed['title'])
                    update_stmt = """UPDATE `rss_feed_contents` SET `content_title`  = '%s', `content_summary` = '%s', `content_md5` = '%s'"""
                    cur.execute(update_stmt %(feed['title'], feed['summary'], feed['md5']))
                    cur.commit()
                      
                except MySQLdb.Error, e:
                    
                    self.db.rollback()
                    print "Raise error : %s" %(e)
                finally:
                    cur.close()
            else:
                print "....feed exists !"
                 
                return True
            
        
        return False
            
    
    def _insert_feed_content_in_db(self):
        
        cur = self.db.cursor()
        print "...insert  %d feed(s)" %(len(self.feeds))
        
        #print self.feeds
        #(`feed_id`, `content_title`, `content_link`, `content_summary`, `content_md5`, `content_addtimne`) 
        try:
            insert_content_stmt = """INSERT INTO  `rss_feed_contents` VALUES(NULL, %s, %s, %s, %s, %s, %s)"""
            
            cur.executemany(insert_content_stmt , self.feeds)
            self.db.commit()      
                       
        except MySQLdb.Error, e:
            
            self.db.rollback()
            print "raise error : %s" %(e)
        
            
                
        finally:
            cur.close()
                
if __name__ == "__main__":
    
    
      t = AddFeedContentThread(1, "http://www.xiami.com/collect/feed")   
      t.start()   
      
      t.join()
      
      print "...####Over"
            
