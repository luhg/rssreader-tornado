#-*-coding:utf-8-*-

import MySQLdb 
import getpass

import time 




#pwd = getpass.getpass("passwod:")
mydb = MySQLdb.connect(
						host = 'localhost', 
						user = 'xxx', 
						passwd= "xxx", 
						db = 'rss_db')
						


cur = mydb.cursor()
#insert_statement = """
#INSERT INTO `rss_users` (`username`, `password`, `email`, `created_on`) 
#VALUES("%s", "%s", "%s", %d);
#"""
#
#create_time = int(time.time())
#print create_time
#print insert_statement % ("John", "123", "thomaslyang@qq.com", create_time)
#try:
#	
#	cur.execute(insert_statement % ("John", "123", "thomaslyang@qq.com", create_time))
#except:
#	raise

query_statement = """SELECT * 
FROM rss_users
WHERE email = '%s' AND password = '%s'"""

print query_statement %("lyanghwy@gmail.com" , "123456")

try:
	command = cur.execute(query_statement %("lyanghwy@gmail.com", "123456" ))
	result = cur.fetchone()
	print result[0], "h   h", command


except MySQLdb.Error, e:
	raise

#mydb.commit()
#mydb.close()
