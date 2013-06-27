#-*-coding:utf-8-*-


import tornado.web
import re
import feedparser

class RssBaseHandler(tornado.web.RequestHandler):
    
    def get(self):
        self.set_header("Content-Type", "application/json")
        self.set_status(404)
        self.write('{"status":"error","msg":"Page not found"}')
        
    @property
    def db(self):
        return self.application.db
    
    def get_current_user(self):
        self.set_header("Content-Type", "application/json")
        email = self.get_secure_cookie("member_auth")
        if not email: return None
        cur = self.db.cursor()
    
        query_statement = """SELECT * FROM rss_users WHERE email = '%s'"""
        command = cur.execute(query_statement %(email))
        return cur.fetchone()
    
    
def EmailIsVaild(email):
    if len(email) > 5:
        return True
    
    return False

def PasswdIsVaild(passwd):
    if  5 < len(passwd) < 17:
        return True
    
    return False

def URLValidator(url):
    
    url_regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if url_regex.match(url):
        return True
    
    return False


def SubscribeVaildator(subscribe):
    
    feed = feedparser.feedparser(subcribe)
    
    if 'version' in feed and feed['version'] != '':
        return True
    
    return False
   
    



