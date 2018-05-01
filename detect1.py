import requests,urllib2,ssl

def api():
	global gender
	global age
	global msg
	global face_count
	ctx = ssl.create_default_context()
	ctx.check_hostname = False
	ctx.verify_mode = ssl.CERT_NONE

	subscription_key = "83a0257e77e848ec95b3bff0adee17cb"
	assert subscription_key
	face_api_url = 'https://westcentralus.api.cognitive.microsoft.com/face/v1.0/detect'
	img_url = 'https://smartfacerec.ddns.net/api/known_people/4.jpg'
	headers = { 'Ocp-Apim-Subscription-Key': subscription_key }
	params = {
			    'returnFaceId': 'true',
			    'returnFaceLandmarks': 'false',
			    'returnFaceAttributes': 'age,gender,headPose,smile,facialHair,glasses,emotion,hair,makeup,occlusion,accessories,blur,exposure,noise',
			}

	response = requests.post(face_api_url, params=params, headers=headers, json={"url": img_url})
	faces = response.json()
	print faces
	print "Total Faces:",len(faces)
	for face in faces:
	    fa = face['faceAttributes']
	    gender = str(fa["gender"].capitalize())
	    age = str(fa["age"])
	    msg = "Face Detected"
	    print "Gender: ",gender, "Age: ", age

api()
