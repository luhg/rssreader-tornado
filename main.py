#-*-coding:utf-8 -*-

import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options
from tornado.escape import json_encode
import os
import MySQLdb

import feedparser
import time 

import RssUtil
from RssUtil import  RssBaseHandler, EmailIsVaild, PasswdIsVaild

from tornado.options import define, options
# define the configure and command-line parser and help

define("port", default = 8080, help  = "run on given port", type = int)
define("mysql_host", default = "localhost", help = "rss database host")
define("mysql_database", default = "rss_db", help = "rss server database name")
define("mysql_user", default = "xxx", help = "rss server database user")
define("mysql_password", default = "xxx", help="rss server database password")
define("mysql_port", default = 3036, help="rss server database port", type = int)
             
    

class LoginHandler(RssBaseHandler):
    
    def get(self):
       # self.set_header("Content-Type", "text/html; charset=utf-8")
        self.render("login.html")
    
    def post(self):
        email = self.get_argument("email", default = None)
        password = self.get_argument("password", default = None)
        print email, password
        if email != None and 5  < len(password) <= 16:
            cur = self.db.cursor()
            query_statement = """SELECT * FROM rss_users WHERE email = '%s' AND password = '%s'"""       
            
            comannd = cur.execute(query_statement %(email, password))
            user = cur.fetchone()
        
        if user:
           
            self.set_secure_cookie("member_auth", user[3])
            self.redirect("/")
            

class RegisterHandler(RssBaseHandler):
    
    def get(self):
        self.render("register.html")

    def post(self):
        username = self.get_argument("username", default = None)
        email = self.get_argument("email", default = None)
        password = self.get_argument("password", default = None)
        verify_password = self.get_argument("verify_password", default = None)
        
        if EmailIsVaild(email) and  password == verify_password and PasswdIsVaild(password):
            cur = self.db.cursor()
            create_user_stmt = """INSERT INTO `rss_users` VALUES(NULL, '%s', '%s', '%s', %d, %d, 0)"""
            stmt = create_user_stmt %(username, password, email, int(time.time()), int(time.time()))
            #self.write(stmt)
            
            try:
                command = cur.execute(stmt )
                
                self.db.commit()
            except:
                self.db.rollback()
            
            
        if command == 1:
                user_query_stmt = """SELECT * FROM rss_users WHERE email = '%s' AND password = '%s'"""  
                command = cur.execute(user_query_stmt %(email, password))
                user = cur.fetchone()
        
        if user:
           
            self.set_secure_cookie("member_auth", user[3])
            self.redirect("/") 
        
        
        
class AddSubscribeHandler(RssBaseHandler):
    
    def get(self):
        
        self.render("addsubscribe.html")
    
    @tornado.web.authenticated
    def post(self):  
        user = self.current_user    
           
        subscribe = self.get_argument("subscribe")
        
        msg_dict = {"status" : "error", 
                    "msg" : "add subcribe failed"}
        
        if RssUtil.URLValidator(subscribe):
            
            d = feedparser.parse(subscribe)
            if 'version' in d and d['version'] != '':
                if 'feed' in d and 'title' in d['feed']:
                    title = d['feed']['title']
                    cur = self.db.cursor()
                    try:
                    
                        cur.execute("CALL addsubscirbe('%s', '%s', %d )" %(subscribe, title , user[0] ))
                        self.db.commit()
                    except MySQLdb.Error, e:
                            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
                    finally:
                        cur.close()
                        msg_dict['status'] = "ok"
                        msg_dict['msg'] = "add subcribe successed!"
    
        
        self.write(json_encode(msg_dict))
    

class DelSubscribeHandler(RssBaseHandler):
    
    def get(self):
        cur = self.db.cursor()
        
        cur.execute("DELETE FROM `rss_user_feeds` WHERE `feed_id` = %d and uid = %d" )

class GetUserCategoriesHandler(RssBaseHandler):

    @tornado.web.authenticated
    def get(self): 
        
        user = self.current_user 
        cate = {'categories' : [],
                    'counts' : 0,
                    'status' : "error",
                    'msg' : u"不能找到该用户" }
        q_stmt = """SELECT * FROM `rss_user_feed_categories` WHERE `uid` = %d"""
        
        try:
            cur = self.db.cursor()
            command = cur.execute(q_stmt %(user[0]))
            
            categories  = cur.fetchall()
            cate = {'categories' : [x[0] for x in categories ],
                    'counts' : len(categories ),
                    'status' : "ok",
                    'msg' : 'all right : )' }
            
            
        except MySQLdb.Error, e:
            cate = {'categories' : [],
                    'counts' : 0,
                    'status' : "error",
                    'msg' : u"不能找到该用户" }
            
        finally:
            cur.close()
        self.content_type = 'application/json' 
        self.write(json_encode(cate))
        
class GetCategoryByNameHandler(RssBaseHandler):
    
    def get(self):
        msg_dict = {"status" : "error", 
                    "msg" : "no data",
                   'subscribes' : []}
        
        self.write(json_encode(msg_dict))
    
    def post(self):
        user = self.current_user
        category_name = self.get_argument("category_name")
        msg_dict = {"status" : "error", 
                    "msg" : "add subcribe failed",
                   'subscribes' : []}
       
            
        if user:
            
            try:
                cur = self.db.cursor()
                cur.execute(""""SELECT * FROM `rss_user_feeds` WHERE `category_name` = '%s and `uid` = %d'""" %(category_name, user[0]) )
                results = cur.fetchall()
                
                msg_dict["status"] =  "Ok"
                msg_dict["msg"]  = "fine"
                
                msg_dict['subscribes'] = [x[1] for x in results]
                
            except MySQLdb.Error, e:
                
                msg_dict['msg'] = e.args[1]  
            
        #self.content_type = 'application/json' 
        self.write(json_encode(msg_dict))
        


class GetSubscribeByFeedIdHandler(RssBaseHandler):
    
    def get(self):
        msg_dict = {"status" : "error", 
                    "msg" : "add subcribe failed",
                   'subscribe_contents' : dict()}
       
        user = self.current_user
        if user:
            feed_id = self.get_arument("feed_id")
            cur =  cur = self.db.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("SELECT lass_access FROM rss_user_feeds WHERE uid = %s AND fee_id = %s" %( user[0], feed_id))
            
            if cur.rowcount == 1:
                try:
                    old_access = cur.fetchone()['last_aceess']
                    cur.execute("CALL  updateAndGetContentsUserFeedContens(%s, %s, %d, %d)" %(user[0], feed_id, old_access, int(time.time())))
                    self.db.commit()
                    
                    contents =  cur.fetchall()
                    msg_dict["status"] =  "Ok"
                    msg_dict["msg"]  = "fine"
                
                    msg_dict['subscribe_contents'] = [x for x in contents]
                    
                except MySQLdb.Error, e:
                    
                    self.rollback()
                    
                finally:
                   cur.close()
            
            
            self.write(json_encode(msg_dict))  
    




class GetContentByIdHandler(RssBaseHandler):
    
    def get(self, content_id ):
        
        user = self.current_user
        
        client_dict = {"status" : "error",
                       "msg" : "Failed",
                       "content": dict()}
        
        
        if user :
            
            try: 
                cur = self.db.cursor()
                
                command = cur.execute("""SELECT * FROM  `rss_feed_contents` WHERE `content_id` = %s""" %(content_id))
                content = None
                if command  == 1:
                    content = cur.fetchone()
                    client_dict['status'] = "ok"
                    client_dict['msg'] = "success get content"
                    client_dict['content'] = {
                                  "content_id": content[0],
                                  "feed_id" : content[1],
                                  "content_title" : content[2],
                                  "content_link": content[3],     
                                  "content_summary": content[4],
                                  "content_md5" : content[5],}
                    self.db.commit()
            except MySQLdb.Error, e:
                    client_dict['msg'] = e.args[1]
                    pass
                
                
            finally:
                cur.close()
       
        
        self.write( json_encode(client_dict) )
        


class AddCollectByContentIdHandler(RssBaseHandler):   
    
    def post(self):
        user = self.curent_user()
        content_id = self.get_argmument("content_id")
        
        client_dict = {"status" : "error",
                       "msg" : "add collect failed"}
        
        if user:
            
            try:
                cur = self.db.cursor()
            
                command = cur.execute("CALL addCollect(%d, %s, %d)" %(user[0], content_id, int(time.time())))
                client_dict['status'] = "ok"
                    
                client_dict['msg'] = cur.fetchone()[0]
                self.db.commit()
            
            except  MySQLdb.Error, e:
                self.db.rollback()
            finally:
                cur.close()
        
        self.write( json_encode(client_dict) )
            
            
        
        

class DelCollectByContentUrlHandler(RssBaseHandler):   
    
    def post(self):
        user = self.curent_user()
        content_url = self.get_argmument("content_url")
        
        client_dict = {"status" : "error",
                       "msg" : "delect collect failed"} 
        
        if user:
            
            try:
                cur = self.db.cursor()
            
                command = cur.execute("""DELETE FROM `rss_user_collcet` WHERE `uid` = %d AND `collect_url` = '%s'""" \
                                      %(user[0], content_url))
                if command == 1 :
                    client_dict['status'] = "ok"
                    client_dict['msg'] = "delete suceess"
                    
                self.db.commit()
            
            except  MySQLdb.Error, e:
                self.db.rollback()
            finally:
                cur.close()
        
        self.write( json_encode(client_dict) )
        
       
class GetCollectHandler(RssBaseHandler):
    
    def get(self):
        user = self.current_user
        
        client_dict = {"status" : "error",
                       "msg" : "please login first",
                       "collects": dict()} 
        
        if user:
            try:
                cur = self.db.cursor(MySQLdb.cursors.DictCursor)
            
                command = cur.execute("""SELECT `collect_url`, `collect_title`, `collect_addtime` FROM `rss_user_collect` WHERE `uid` = %d ORDER BY `collect_addtime`""" \
                                      %(user[0]))
                if cur.rowcount > 0 :
                    client_dict['status'] = "ok"
                    client_dict['msg'] = "fetch collect suceess"
                    collects = cur.fetchall()
                    client_dict["collects"] = [collect for collect in collects]
                    
            
            except  MySQLdb.Error, e:
                self.db.rollback()
            finally:
                cur.close()
        
        self.write( json_encode(client_dict) )
            
        
    
        
        

class ChangeCategory(RssBaseHandler):
    
    def post(self):
        user = self.current_user
        feed_id = self.get_argument("feed_id")
        new_category = self.get_argument("category")
        
        if user and new_cateogry != None:
            
            try:
                cur = self.db.cursor()
                cur.execute("""UPDATE `rss_user_feeds` SET `category_name` = '%s' WHERE `feed_id` = %d and `uid` = %d"""\
                            %(new_category, feed_id, user[0] ))
                self.db.commit()
            
            except MySQLdb.Error, e:
                
                pass
    
    

        

class RenameCategory(RssBaseHandler):
    
     def post(self):
         user = self.current_user
         feed_id = self.get_argument("feed_id")
         old_category = self.get_argument("old_category")
         new_category = self.get_argument("category")
        
         if user and new_cateogry != None:
            
            try:
                cur = self.db.cursor()
                cur.execute("""UPDATE `rss_user_feeds` SET `category_name` = '%s' WHERE `category_name`  = '%s' and `uid` = %d"""\
                            %(new_category, feed_id, user[0] ))
                self.db.commit()
            
            except MySQLdb.Error, e:
                
                pass
        
    



class DelCategory(RssBaseHandler):    
    
    def post(self):
        category = self.get_argument("category_name")
        if user and category != None:
            
            try:
                cur = self.db.cursor()
                cur.execute("""UPDATE `rss_user_feeds` SET `category_name` = '其他' WHERE `category_name`  = '%s' and `uid` = %d"""\
                            %(new_category, feed_id, user[0] ))
                self.db.commit()
            
            except MySQLdb.Error, e:
                    pass
        
        
        
    

class WelcomeHandler(RssBaseHandler):
    
    @tornado.web.authenticated
    def get(self):
        self.render("index.html", user = self.current_user)
        
class LogoutHandler(RssBaseHandler):
    
    def post(self):
        
        if (self.get_argument("logout", None)):
            self.clear_cookie("member_auth")
            self.redirect("/")
        else:
            self.render("logout.html")


    
    
class IndexHandler(tornado.web.RequestHandler):
    
    def get(self):
        self.write("Hello world")
    

        
class NopermHandler(RssBaseHandler):
    def get(self):
      
        self.redirect("/error")

class ErrorHandler(RssBaseHandler):
    def get(self):
        self.render("nopressiom.json")
    
class Application(tornado.web.Application):
    
    def __init__(self):
        
        #define and custom url route
        handlers = [(r'/', WelcomeHandler),
                    (r'/login', LoginHandler),
                    (r'/logout', LogoutHandler),
                    (r'/register', RegisterHandler),
                    (r'/categories', GetUserCategoriesHandler ),
                    (r"/category", GetCategoryByNameHandler),
                    (r'/noperm', NopermHandler),
                    (r'/error', ErrorHandler ),
                    (r'/addsubscribe', AddSubscribeHandler ),
                    (r'/subscribe/content/(\d+)', GetContentByIdHandler),
                    (r'/collect', GetCollectHandler),
                    (r'/addcollect',AddCollectByContentIdHandler ),
                    (r'/.*', ErrorHandler),
           
                #(r'/login', tornado.web.StaticFileHandler, {'path': os.path.join(os.path.dirname(__file__), "static")}),
                ]
        
        #server setting configure
        settings = dict(
                    static_path = os.path.join(os.path.dirname(__file__), "static"),
                    template_path = os.path.join(os.path.dirname(__file__), "templates"),
                    debug = True,
                    cookie_secret = "bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=",
                    login_url = r'/noperm',
                   )
        
        tornado.web.Application.__init__(self,handlers, **settings)
        
        #database handler
        self.db = MySQLdb.Connect(
            host=options.mysql_host, db=options.mysql_database,
            user=options.mysql_user, passwd=options.mysql_password,
            use_unicode=True, 
            charset="utf8")
        
        

if __name__ == "__main__":
    
    print  os.path.join(os.path.dirname(__file__), "static")
    tornado.options.parse_command_line()
    
    server = tornado.httpserver.HTTPServer(Application())
    
    server.listen(options.port)
    
    tornado.ioloop.IOLoop.instance().start()
    
    
