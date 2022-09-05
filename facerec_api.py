import torch,cv2,sys,time,os
import numpy as np
import face_recognition
from PIL import Image
import threading
from flask import Flask, jsonify, request
from os import listdir
from os.path import isfile, join
from pathlib import Path

# creating a Flask app
app = Flask(__name__)


known_images = []
known_face_encodings = []
known_face_ids = []
matched_faceids = []

def load_faces():
    print("[info]: Loading Known Faces | ",time.time())
    #####Load all face ids##############################
    known_images = [f for f in listdir("known") if isfile(join("known", f))]
    for known_image in known_images:
        print(join("known", known_image))
        face_img = face_recognition.load_image_file(join("known", known_image))
        face_ecod = face_recognition.face_encodings(face_img)[0]
        known_face_encodings.append(face_ecod)
        face_id = known_image.split(".")[0]
        known_face_ids.append(face_id)        
    #print(known_face_encodings)
    #print(known_face_ids)
    print("[info]: Finished Loading Known Faces | ",time.time())
####################################################
def save_face(file):
    frame = cv2.imread(file)
    face_id = str(time.time())
    face_idd = face_id.split(".")
    face_id = str(face_idd[0])+str(face_idd[1])
    cv2.imwrite(os.path.join('known',face_id+'.jpg'),frame)
    
    ##RESET FACEREC KNOWN Datasets#########################
    known_images.clear()
    known_face_encodings.clear()
    known_face_ids.clear()
    matched_faceids.clear()    
    load_faces()
    
    return(face_id)
    
def check_face(file):
    frame = cv2.imread(file)
    frame = frame[:, :, ::-1]
    face_encodings = face_recognition.face_encodings(frame)
    if len(face_encodings)>0:
        return(True)
    else:
        return(False)

def facerec(file):
    matched_faceids.clear()
    frame = cv2.imread(file)
    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = frame #cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]      
    face_encodings = face_recognition.face_encodings(rgb_small_frame)
    if len(face_encodings)>0:
        # Facerec Core API
        matches = face_recognition.compare_faces(known_face_encodings, face_encodings)
    
        #Finding Face ID of matched True
        matched_indexs = [i for i, x in enumerate(matches) if x]
        for matched_index in matched_indexs:
            matched_faceids.append(known_face_ids[matched_index])
        return(matched_faceids)
    else:
        return('None')

@app.route('/api', methods = ['GET', 'POST'])
def home():
    if(request.method == 'GET'):  
        data = "Pehchan2.1- Smart Facerecognition System"
        return jsonify({'data': data})
  
@app.route('/api/pehchan/login', methods = ['GET', 'POST'])
def api_login():
    params = request.args
    face_url = params.get('face_url')    
    token= params.get('token')
    my_file = Path(face_url)
    if token == "pehchan2.1SmartFacerecognitionSystem":
        if my_file.is_file():
            face_id=facerec(face_url)   
            confidence=None
            return jsonify({'API TOKEN':token,
                                'STATUS':"Success",
                                'IMAGE_URL':face_url,
                                'FACE_ID':face_id,
                                'CONFIDENCE':confidence})
        else:
            return jsonify({'API TOKEN':token,
                                'STATUS':"Invalid IMAGE_URL"})
                            
    else:
        return jsonify({'API TOKEN':token,
                            'STATUS':"Invalid Token"})
                            
########################################################################
@app.route('/api/pehchan/register', methods = ['GET', 'POST'])
def api_register():
    params = request.args
    confidence=None
    face_url = params.get('face_url')    
    token= params.get('token')
    my_file = Path(face_url)
    if token == "pehchan2.1SmartFacerecognitionSystem":
        if my_file.is_file():
            face_stat = check_face(face_url)
            if face_stat==True:
                face_ids=facerec(face_url) 
                #print(face_ids)
                if len(face_ids)==0:
                    face_id=save_face(face_url)
                    return jsonify({'API TOKEN':token,
                                        'STATUS':"Success",
                                        'IMAGE_URL':face_url,
                                        'FACE_ID':face_id})
                else:
                    return jsonify({'API TOKEN':token,
                                    'STATUS':"Face Exists",
                                    'FACE_ID':face_ids})
                                    
                                        
            if face_stat==False: 
                return jsonify({'API TOKEN':token,
                                    'STATUS':"No Face Found"})
        else:
            return jsonify({'API TOKEN':token,
                                'STATUS':"Invalid IMAGE_URL"})
                            
    else:
        return jsonify({'API TOKEN':token,
                            'STATUS':"Invalid Token"})
                            
if __name__ == "__main__":     
    load_faces()
    app.run(host='0.0.0.0', port=5000,debug = True)
