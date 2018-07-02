print "CODED BY VSL Creations | email@vslcreations.com"
print "-----------------------------------------------"
print "ENTRY COUNTER CAMERA\n"

print "ENTER CAMERA URL TYPE\n1.IP CAMERA HTTP URL\n2.IP CAMERA RTSP URL/DIRECT VIDEO HTTP URL/LOCAL PATH"
ch = raw_input("CHOICE:")
print "----------------------"

print "ENTER SERVER URL TYPE\n1.VPS URL(Admin Use Only)\n2.FTP URL(Recommended for Client Use)"
ch1 = raw_input("CHOICE:")
print "----------------------"

import cv2,sys,os,os.path
import datetime,ftplib
import threading,csv
import urllib2,ssl,time
import numpy as np



offset=50
#eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
font = cv2.FONT_HERSHEY_SIMPLEX

imgid = 0
imgid1 = 0
for line in open('in/logentry.txt', 'r'):
        imgid=int(line)

if imgid==0:
        imgid = 1
print "Current IMG ID:",imgid

imgid1 = imgid
ext = ".jpg"
counter = 0
running = 1
finalimgid = 0

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Fancy box drawing function by Dan Masek
def draw_border(img, pt1, pt2, color, thickness, r, d):
    x1, y1 = pt1
    x2, y2 = pt2

    # Top left drawing
    cv2.line(img, (x1 + r, y1), (x1 + r + d, y1), color, thickness)
    cv2.line(img, (x1, y1 + r), (x1, y1 + r + d), color, thickness)
    cv2.ellipse(img, (x1 + r, y1 + r), (r, r), 180, 0, 90, color, thickness)

    # Top right drawing
    cv2.line(img, (x2 - r, y1), (x2 - r - d, y1), color, thickness)
    cv2.line(img, (x2, y1 + r), (x2, y1 + r + d), color, thickness)
    cv2.ellipse(img, (x2 - r, y1 + r), (r, r), 270, 0, 90, color, thickness)

    # Bottom left drawing
    cv2.line(img, (x1 + r, y2), (x1 + r + d, y2), color, thickness)
    cv2.line(img, (x1, y2 - r), (x1, y2 - r - d), color, thickness)
    cv2.ellipse(img, (x1 + r, y2 - r), (r, r), 90, 0, 90, color, thickness)

    # Bottom right drawing
    cv2.line(img, (x2 - r, y2), (x2 - r - d, y2), color, thickness)
    cv2.line(img, (x2, y2 - r), (x2, y2 - r - d), color, thickness)
    cv2.ellipse(img, (x2 - r, y2 - r), (r, r), 0, 0, 90, color, thickness)
    

def ftp():
        global running,finalimgid,imgid1
	imgid = imgid1
        global ctx

        while True:
		time.sleep(0.2)
		#print 'in/entryimg-'+str(imgid)+ext
		if os.path.exists('in/entryimg-'+str(imgid)+ext):
                        intime = str(datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S"))
                        if ch1=='1':
                                apiurl = "https://smartfacerec.ddns.net/api/entryapi.php?url=http://67.211.45.136:8010/retailvision/in/entryimg-"+str(imgid)+ext+"&intime="+intime+"&id="+str(imgid)
                        if ch1=='2':
                                session = ftplib.FTP('ranjandentalclinic.com','api@ranjandentalclinic.com','vslcreations.com')       
                                file = open('in/entryimg-'+str(imgid)+ext,'rb')                  # file to send
                                filedir = 'STOR '+'in/entryimg-'+str(imgid)+ext
                                session.storbinary(filedir, file)     # send the file
                                #print 'in/entryimg-'+str(imgid1)+ext+' | STORED TO SERVER'
                                file.close()                                    # close file and FTP
                                session.quit()
                                apiurl = "https://smartfacerec.ddns.net/api/entryapi.php?url=http://ranjandentalclinic.com/api/in/entryimg-"+str(imgid)+ext+"&intime="+intime+"&id="+str(imgid)
			#print apiurl
			
			try:
				response = urllib2.urlopen(apiurl, context=ctx)
				data = response.read()
				print "ID:",imgid,"| ",data
				if data == "FACE EXISTS":
					os.remove('in/entryimg-'+str(imgid)+ext)
			except urllib2.HTTPError:
				pass

			imgid = imgid+1
			finalimgid = imgid
			#print "entryimg-"+str(imgid1)+ext+" | FACE DETECTED & STORED TO CLOUD"

		if running==0:
		   break
		
		else:
			print "Waiting for FACE...\n"
			while True:
				if os.path.exists('in/entryimg-'+str(imgid)+ext):
					break
		


def variance_of_laplacian(image):
	# compute the Laplacian of the image and then return the focus
	# measure, which is simply the variance of the Laplacian
	return cv2.Laplacian(image, cv2.CV_64F).var()

msg = 'FACE DETECTED'

if ch=='2':
    host = raw_input("ENTER URL:")
    print '2.Streaming: ' + host
    cam = cv2.VideoCapture(host)
    fps = cam.get(cv2.CAP_PROP_FPS)
    width = cam.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cam.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print "FPS:",fps,"\nWidth:",width,"\nHeight:",height    
    cam.set(cv2.CAP_PROP_FPS, fps)

    key = int(1000/fps)
    
    if key>10:
        key = key-10
    else:
        key = 1
    #print "Wait Key:",key
    
    #multi-threading
    t = threading.Thread(target=ftp)
    t.start()

    # keep looping until the 'q' key is pressed
    while True:
            imgname = 'entryimg-'

            (grabbed, i) = cam.read()
            if not grabbed:
                break

            small_frame = cv2.resize(i, (640, 400))
                    
            img = small_frame
            orig_img = img.copy()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            fm = variance_of_laplacian(gray)
            #print type(fm)
            if fm>20:
                    cv2_faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                    for (x,y,w,h) in cv2_faces:
                        #cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
                        draw_border(img, (x, y),(x+w,y+h), (162, 255, 0), 2, 10, 10)
                        msg = 'FACE DETECTED'    
                        counter = counter+0.1
                        roi_color = orig_img[y:y+h, x:x+w]
                        cv2.putText(img,msg,(x,y), font, 1,(255,255,255),2,cv2.LINE_AA)
                            
                    
                    #Store img if face detected
                    if counter>0.3:
                        imgname = imgname + str(imgid) + ext
                        cv2.imwrite('in/'+imgname,roi_color)
                        #ftp()
                        msg = 'FACE STORED'    
                        imgid = imgid+1 
                        imgname = 'entryimg-'
                        counter = 0
                    
            cv2.imshow('img',img)                
            
            if cv2.waitKey(key) & 0xff == ord('q'):
                running = 0
                break
    cam.release()
    
elif ch=='1':
    host = raw_input("ENTER URL(e.g-http://192.168.0.105:8080/video):")
    print '1.Streaming: ' + host
    #print type(host)
    stream=urllib2.urlopen(str(host))
    bytes=''

    #multi-threading
    t = threading.Thread(target=ftp)
    t.start()

    # keep looping until the 'q' key is pressed
    while True:
            imgname = 'entryimg-'
            # load the image, clone it, and setup the mouse callback function
            bytes+=stream.read(1024)
            a = bytes.find('\xff\xd8')
            b = bytes.find('\xff\xd9')
            if a!=-1 and b!=-1:
                    jpg = bytes[a:b+2]
                    bytes= bytes[b+2:]
                    i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.IMREAD_COLOR)
                    small_frame = cv2.resize(i, (600, 340))
                    
                    img = small_frame
                    orig_img = img.copy()
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

                    fm = variance_of_laplacian(gray)
                    #print type(fm)
                    if fm>20:
                            cv2_faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                            for (x,y,w,h) in cv2_faces:
                                #cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
                                draw_border(img, (x, y),(x+w,y+h), (162, 255, 0), 2, 10, 10)
                                msg = 'FACE FOUND'
                                cv2.putText(img,msg,(x,y), font, 1,(255,255,255),2,cv2.LINE_AA)     
                                counter = counter+0.1
                                roi_color = orig_img[y:y+h, x:x+w]
                                #print counter

                            #Store img if face detected
                            if counter>0.3:
                                imgname = imgname + str(imgid) + ext
                                cv2.imwrite('in/'+imgname,roi_color)
                                msg = 'FACE STORED'                                    
                                imgid = imgid+1 
                                imgname = 'entryimg-'
                                counter = 0
                                
                                    
                            cv2.imshow('img',img)                                     
                    
                    if cv2.waitKey(1) & 0xff == ord('q'):
                        running = 0
                        break
else:
    print "WRONG CHOICE-Start Again!"


f = open('in/logentry.txt', 'w')
f.write(str(finalimgid))
f.close()
cv2.destroyAllWindows()
