from PyQt4 import QtCore, QtGui, uic
import sys
import cv2
import numpy as np
import threading
import time
import Queue
import imutils
import serial,time 
 
running = False
capture_thread = None
form_class = uic.loadUiType("gui.ui")[0]
q = Queue.Queue()
  
msgstat = ""
 
def grab(cam, queue, width, height, fps):
    global running
    capture = cv2.VideoCapture(1)
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
 
        self.pushButton.clicked.connect(self.start_clicked)
	#self.stopButton.clicked.connect(self.stop_clicked)
         
        self.window_width = self.widget.frameSize().width()
        self.window_height = self.widget.frameSize().height()
        self.widget = OwnImageWidget(self.widget)       
 
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1)
 
 
    def start_clicked(self):
        global running
        running = True
        capture_thread.start()
        self.pushButton.setEnabled(False)
        #self.pushButton.setText('Initializing...')
 
    def stop_clicked(self):
	global running
        running = False
        sys.exit()
 
    def step1(self):
	    global img
	    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

	    template = cv2.imread('box5.png',0)
            w, h = template.shape[::-1]
	    res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
            threshold = 0.8
            loc = np.where( res >= threshold)
	    
            msg = "Foam1"
            cv2.rectangle(img, (170,200), (170 + 58, 200 + 51), (255,0,0), 2)
            cv2.putText(img, msg, (170, 270), cv2.FONT_HERSHEY_SIMPLEX,0.5, (255, 0, 0), 2)
	    
            for pt in zip(*loc[::-1]):
		    #cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0,255,0), 2)
		    cv2.rectangle(img, (170,200), (170 + 58, 200 + 51), (0,255,0), 2)
		    #wt=ser.readline()
		    #wt=wt.strip('\n')
		    msg = "Detected"
		    self.widget_18.setStyleSheet("border-image: url(img/icon7G.png);")
		    self.textBrowser.setText("Connected to Servers...\n\nOutside Foam detected")
		    cv2.putText(img, msg, (170-50, 150), cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 255, 0), 2)
	
	
	#end for
	    
            height, width, bpc = img.shape
            bpl = bpc * width
            image = QtGui.QImage(img.data, width, height, bpl, QtGui.QImage.Format_RGB888)
            self.widget.setImage(image)
 
	
    def step2(self):
	    global img
	    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

	    template = cv2.imread('box.png',0)
            w, h = template.shape[::-1]
	    res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
            threshold = 0.8
            loc = np.where( res >= threshold)
	    
            msg = "Foam2"
            cv2.rectangle(img, (300,180), (300 + 58, 180 + 51), (255,0,0), 2)
            cv2.putText(img, msg, (300, 250), cv2.FONT_HERSHEY_SIMPLEX,0.5, (255, 0, 0), 2)
	    timer = 0.0
            for pt in zip(*loc[::-1]):
		    #cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0,255,0), 2)
		    cv2.rectangle(img, (300,180), (300 + 58, 180 + 51), (0,255,0), 2)
		    #wt=ser.readline()
		    #wt=wt.strip('\n')
		    msg = "Detected"
		    self.widget_18.setStyleSheet("border-image: url(img/icon7G.png);")
		    self.textBrowser.setText("Connected to Servers...\n\nOutside Foam detected")
		    cv2.putText(img, msg, (300-50, 180), cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 255, 0), 2)   
	   
	#end for
	    
            height, width, bpc = img.shape
            bpl = bpc * width
            image = QtGui.QImage(img.data, width, height, bpl, QtGui.QImage.Format_RGB888)
            self.widget.setImage(image)
 

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
            self.step1()
	    self.step2()

    def closeEvent(self, event):
        global running
        running = False
 
 
 
capture_thread = threading.Thread(target=grab, args = (0, q, 1920, 1080, 30))
 
app = QtGui.QApplication(sys.argv)
w = MyWindowClass(None)
w.setWindowTitle('LG- Monitoring System')
w.show()
app.exec_()
