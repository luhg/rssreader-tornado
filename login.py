#-*-coding:utf-8-*-

import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.options

import MySQLdb
import time
import os.path

from tornado.options import define, options

define("port", default = 8080, help ="run on given port", type = int)

class LoginHandler(tornado.web.RequestHandler):
    
    def get(self):
        self.render("login.html")
    
    def post(self):
        username = self.get_argument("username", default = "anyousmous")
        email = self.get_argument("email", default = "123@example.com")
        password = self.get_argument("password", default = "None")
        self.write(email + " " + password)
        

class IndexHandler(tornado.web.RequestHandler):
    
    def get(self):
        self.write("Hello world")
    
  
             
class Application(tornado.web.Application):
    
    def __init__(self):
        handlers = [(r'/login$', LoginHandler),
                    (r'/', IndexHandler),
                #(r'/login', tornado.web.StaticFileHandler, {'path': os.path.join(os.path.dirname(__file__), "static")}),
                ]
        settings = dict(
                    static_path = os.path.join(os.path.dirname(__file__), "static"),
                    template_path = os.path.join(os.path.dirname(__file__), "templates"),
                    debug = True,
                   )
        tornado.web.Application.__init__(self,handlers, **settings)
        
        
        

if __name__ == "__main__":
    #print  os.path.join(os.path.dirname(__file__), "static")
    tornado.options.parse_command_line()
    
    
    
    server = tornado.httpserver.HTTPServer(Application())
    
    server.listen(options.port)
    
    tornado.ioloop.IOLoop.instance().start()
    
    
    
    
    
