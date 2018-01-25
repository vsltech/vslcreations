#Coded By: Vishal Aditya | Embedded Software Engineer | Miisky Technovation Pvt. Ltd.	

import MySQLdb

# Open database connection
db = MySQLdb.connect("45.127.102.254","miiskyroot","miisky@123","miisky123" )

# prepare a cursor object using cursor() method
cursor = db.cursor()

sql = "SELECT * FROM svasth_connect where current_dat='2018-01-24'"

count = 0
try:
   # Execute the SQL command
   cursor.execute(sql)
   # Fetch all the rows in a list of lists.
   results = cursor.fetchall()
   for row in results:
      '''fname = row[0]
      lname = row[1]
      age = row[2]
      sex = row[3]
      income = row[4]
      # Now print fetched result
      print "fname=%s,lname=%s,age=%d,sex=%s,income=%d" % \
             (fname, lname, age, sex, income )'''
      count = count+1
      print row,"\n"
except:
   print "Error: unable to fecth data"

# disconnect from server
db.close()
