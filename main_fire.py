import torch,cv2,sys
import numpy as np
from PIL import Image

model = torch.hub.load('yolov5', 'custom', 'pytorch/object-detection/yolov5/experiment1/best.pt', source='local')  # local repo


def fire_detector(url,w,h):        
    vid = cv2.VideoCapture(url)
    while(True):
        ret, frame = vid.read()
        if ret:
            frame = cv2.resize(frame, (w, h),interpolation = cv2.INTER_NEAREST)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            results = model(frame)  # inference
            results.render()  # updates results.imgs with boxes and labels
            res = results.pandas().xyxy[0]
            predi = res['name'].values.astype(str)
            confi = res['confidence'].values.astype(str)
            if len(predi)>0:
                print(predi[0],",",confi[0])
            else:
                print("None")
                
            result = np.asarray(results.imgs[0])
            
            result = cv2.cvtColor(result, cv2.COLOR_RGB2BGR)
            cv2.imshow('FireDetector', result)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    # After the loop release the cap object
    vid.release()
    # Destroy all the windows
    cv2.destroyAllWindows()
    
import threading
#rtsp://192.168.0.220:554/live/0/MAIN
    
if __name__ == "__main__":
    url = sys.argv[1]
    if url=="1":
        url=int(url)
    
    t2 = threading.Thread(target=fire_detector, args=[url,640,480])
    t2.start()
