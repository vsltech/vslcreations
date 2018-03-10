#! /usr/bin/python

from PyQt4 import QtCore, QtGui, uic
import sys
import cv2
import numpy as np
import threading
import time
import Queue
import imutils
import serial,time,MySQLdb,datetime

#table: 
'''
ser = serial.Serial(
            port='/dev/ttyUSB0',\
            baudrate=9600,\
            parity=serial.PARITY_NONE,\
            stopbits=serial.STOPBITS_ONE,\
            bytesize=serial.EIGHTBITS,\
                timeout=0)

print"connected to: " + ser.portstr
wt1 = 0.0
'''


running = False
capture_thread = None
form_class = uic.loadUiType("gas_gui.ui")[0]
q = Queue.Queue()
  
msgstat = ""
step1status = 0
step2status = 0
wt1 = 0.0
wt2 = 0.0
lcl = 0.0
ucl = 0.0
ucl_rng = 0.0
lcl_rng = 0.0
frequency = 0
checkpointno = 0
checkpoint_value = 0.0
dateTime = datetime.datetime(2018,1,20,8,00,00)
checkpoint_value_check = ""
colour_code = ""
shiftstarttime = ""
shiftendtime = ""
timeslot = "08:00AM"
avg = 0.0
rng = 0.0

def isfloat(value):
        try:
    		float(value)
    		return True
  	except:
    		return False

'''
db = MySQLdb.connect(host="localhost",  # your host 
                     user="root",       # username
                     passwd="",     # password
                     db="timecheck")   # name of the database
# Create a Cursor object to execute queries.
cur = db.cursor()
# Select data from table using SQL query.
cur.execute("SELECT * FROM checkpoints where parameter_title='Gel Time Head L MC-1'")
# print the first and second columns      
for row in cur.fetchall() :
	lcl= float(row[4])
	ucl=float(row[5])
	frequency=int(row[17])
	checkpointno=int(row[2])
	dateTime=row[31]

def writedb():
	global running
	db1 = MySQLdb.connect(host="localhost",  # your host 
		             user="root",       # username
		             passwd="vslcreations.com",     # password
		             db="timecheck")   # name of the database
	# Create a Cursor object to execute queries.
	cur = db1.cursor()
        running = False
	cur.execute("INSERT INTO `checkpoints_response` (`cr_id`, `checkpoint_id`, `lcl`, `ucl`, `2cl`, `1cl`, `-2cl`, `-1cl`, `centerline`, `ucl_rng`, `lcl_rng`, `cl_rng`, `machine_name`, `checkpoint_value`, `checkpoint_value_check`, `date`, `colour_code`, `time_slot`, `avg`, `rng`, `na`) VALUES (NULL, %s, %s, %s, '0', '0', '0', '0', '0', '0', '0', '0', '0', %s, %s, %s, '#ffff', %s, '0', '0', '-9999')",(checkpointno,lcl,ucl,checkpoint_value,checkpoint_value_check,dateTime,timeslot))
	db1.commit()
	print "Inserted"
	#db.close()
	#sys.exit()
'''	
 
def grab(cam, queue, width, height, fps):
    global running
    capture = cv2.VideoCapture(0)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    capture.set(cv2.CAP_PROP_FPS, fps)
 
    while(running):
        frame = {}        
        capture.grab()
        retval, img = capture.retrieve(0)
        frame["img"] = img
 
        if queue.qsize() < 10:
            queue.put(frame)
        else:
            print queue.qsize()
 
class OwnImageWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(OwnImageWidget, self).__init__(parent)
        self.image = None
 
    def setImage(self, image):
        self.image = image
        sz = image.size()
        self.setMinimumSize(sz)
        self.update()
 
    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        if self.image:
            qp.drawImage(QtCore.QPoint(0, 0), self.image)
        qp.end()
 
 
 
class MyWindowClass(QtGui.QMainWindow, form_class):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setupUi(self)

	global lcl
	global ucl
	global frequency 
        self.pushButton.clicked.connect(self.start_clicked)
	#self.stopButton.clicked.connect(self.stop_clicked)
         
        self.window_width = self.widget.frameSize().width()
        self.window_height = self.widget.frameSize().height()
        self.widget = OwnImageWidget(self.widget)       
 
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1)

	self.label_4.setText(str(frequency))	
	
 	self.label_6.setText('8:00AM')
	self.label_9.setText('11:00AM')
 
 
    def start_clicked(self):
        global running
        running = True
        capture_thread.start()
        self.pushButton.setEnabled(False)
        #self.pushButton.setText('Initializing...')
	self.widget_16.setStyleSheet("border-image: url(img/b0G.png);")


    def stop_clicked(self):
	global running
        running = False
        sys.exit()
	
    def weight1(self):
	global wt1
	#wt=ser.readline()
	wt = 4.5
	if(isfloat(wt)):
		wt1=float(wt)
		#print wt1
		self.widget_11.setStyleSheet("border-image: url(img/b2G.png);")
		self.widget_8.setStyleSheet("border-image: url(img/nextG.png);")
		self.widget_12.setStyleSheet("border-image: url(img/nextG.png);")
		self.textBrowser.setText("Connected to Servers...\n\nAir Weight Measured: "+str(wt1)+"g")
		self.label_15.setText(str(wt1)+"g")
		self.label_7.setText("Task Status: Keep Foam1 detected untill weight is stable")


    def step1(self):
	    global img
	    global step1status
	    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

	    template = cv2.imread('box11.png',0)
            w, h = template.shape[::-1]
	    res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
            threshold = 0.8
            loc = np.where( res >= threshold)
	    
            msg = "Foam1"
            cv2.rectangle(img, (115,150), (115 + 100, 150 + 100), (255,0,0), 2)
            cv2.putText(img, msg, (115, 270), cv2.FONT_HERSHEY_SIMPLEX,0.5, (255, 0, 0), 2)
	    self.label_7.setText("Task Status: Place foam outside water Foam1 untill it's color turns green")
            for pt in zip(*loc[::-1]):
		    #cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0,255,0), 2)
		    cv2.rectangle(img, (115,150), (115 + 100, 150 + 100), (0,255,0), 2)
		    #wt=ser.readline()
		    #wt=wt.strip('\n')
		    msg = "Detected"
		    #self.widget_18.setStyleSheet("border-image: url(img/icon7G.png);")
		    self.widget_3.setStyleSheet("border-image: url(img/b1G.png);")
	            self.widget_15.setStyleSheet("border-image: url(img/nextG.png);")
		    self.weight1()
		    self.textBrowser.setText("Connected to Servers...\n\nOutside Foam detected")
		    cv2.putText(img, msg, (170-50, 150), cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 255, 0), 2)
		    step1status = 1
	
	
	#end for
	    
            height, width, bpc = img.shape
            bpl = bpc * width
            image = QtGui.QImage(img.data, width, height, bpl, QtGui.QImage.Format_RGB888)
            self.widget.setImage(image)
 
	

    def calculate(self):
	global wt1
	global wt2
	global lcl
	global ucl
	global checkpoint_value
	global checkpoint_value_check
	if(wt1!=0.00 and wt2!=0.00):
		checkpoint_value = (wt1/wt2)*1000
		self.textBrowser.setText("Connected to Servers...\n\nCheck-point Value: "+str(checkpoint_value))
		self.widget_4.setStyleSheet("border-image: url(img/b5G.png);")
		self.widget_5.setStyleSheet("border-image: url(img/nextG.png);")

		self.label_19.setText(str(checkpoint_value))
		if(checkpoint_value>=lcl and checkpoint_value<=ucl):
			self.textBrowser.setText("Data Sent to Servers...\n\nTest Status: Pass")
			
			self.widget_18.setStyleSheet("border-image: url(img/icon7G.png);")
			self.widget_9.setStyleSheet("border-image: url(img/b6G.png);")
			self.widget_10.setStyleSheet("border-image: url(img/nextG.png);")
			self.widget_17.setStyleSheet("border-image: url(img/b7G.png);")
			checkpoint_value_check = 'OK'
			#writedb()
		else:
			self.textBrowser.setText("Connected to Server...\n\nTest Status: Fail")
			
	 		self.widget_18.setStyleSheet("border-image: url(img/icon7R.png);")
			self.widget_9.setStyleSheet("border-image: url(img/b6G.png);")
			self.widget_10.setStyleSheet("border-image: url(img/nextG.png);")
			self.widget_17.setStyleSheet("border-image: url(img/b7R.png);")
			checkpoint_value_check = 'NG'
			#writedb()

    def update_frame(self):
        if not q.empty():
            self.pushButton.setText('Start Monitoring')
	    self.textBrowser.setText("Connected to Servers...")
            frame = q.get()
            global img 
	    img = frame["img"]
 
            img_height, img_width, img_colors = img.shape
            scale_w = float(self.window_width) / float(img_width)
            scale_h = float(self.window_height) / float(img_height)
            scale = min([scale_w, scale_h])
 
            if scale == 0:
		    scale = 1
	    img = imutils.resize(img, width=600)
	    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
	    #call step1             
            if step1status==0:
		self.step1()
	    

    def closeEvent(self, event):
        global running
        running = False
 
 
 
capture_thread = threading.Thread(target=grab, args = (0, q, 1920, 1080, 30))
 
app = QtGui.QApplication(sys.argv)
w = MyWindowClass(None)
w.setWindowTitle('LG- Gas Monitoring System')
w.show()
app.exec_()
