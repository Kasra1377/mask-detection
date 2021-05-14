#!/usr/bin/env python
# coding: utf-8

# In[1]:


from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
import numpy as np
import cv2
import os


# In[ ]:


model = load_model("\mask-detection.model")
prototxtPath = "deploy.prototxt"
weightsPath = "res10_300x300_ssd_iter_140000.caffemodel"


# In[3]:


net=cv2.dnn.readNet(prototxtPath , weightsPath)


# In[4]:


def readImage(imagePath):
  #image = cv2.imread(imagePath)
  image = cv2.resize(imagePath , (400 , 300))
  h , w , _ = image.shape
  blob = cv2.dnn.blobFromImage(image,1.0,(300,300),(104.0,177.0,123.0))
  net.setInput(blob)
  detections=net.forward()
  count_persons = 0
  count_mask = 0
  count_withoutmask = 0
  for i in range(0 , detections.shape[2]):
    confidence = detections[0,0,i,2]
  
    if confidence > 0.5:
        count_persons += 1
        box = detections[0,0,i,3:7] * np.array([w , h , w , h])
        (startX , startY , endX , endY) = box.astype("int")
        
        (startX , startY) = (max(0,startX) , max(0,startY))
        (endX , endY) = (min(w-1,endX) , min(h-1,endY))
        
        face = image[startY : endY, startX : endX]
        face = cv2.cvtColor(face , cv2.COLOR_BGR2RGB)
        face = cv2.resize(face , (224 , 224))
        face = img_to_array(face)
        face = preprocess_input(face)
        face = np.expand_dims(face,axis = 0)
        (mask , withoutMask) = model.predict(face)[0]
        
        if mask > withoutMask:
          label = "Mask"
          count_mask += 1
        else:
          label = "No Mask"
          count_withoutmask += 1

        color = (0 , 255 , 0) if label == "Mask" else (0 , 0 , 255)
        label = "{}: {:.2f}%".format(label , max(mask,withoutMask) * 100)
        
        cv2.putText(image , label , (startX , startY-10) , cv2.FONT_HERSHEY_SIMPLEX , 0.45 , color , 2)
        cv2.rectangle(image , (startX , startY) , (endX , endY) , color , 2)  

  cv2.putText(image , "Person(s) : {}".format(count_persons) , (0 , h - 30) , cv2.FONT_HERSHEY_SIMPLEX , 0.45 , (0 , 255 , 255) , 1)
  cv2.putText(image , "With mask : {}".format(count_mask) , (0 , h - 15) , cv2.FONT_HERSHEY_SIMPLEX , 0.45 , (0 , 255 , 255) , 1)
  cv2.putText(image , "Without mask : {}".format(count_withoutmask)  , (0 , h) , cv2.FONT_HERSHEY_SIMPLEX , 0.45 , (0 , 255 , 255) , 1)      
  #cv2.imshow("frame" , image)
  return image
    
  cv2.waitKey(0)
  cv2.destroyAllWindows()


# In[5]:


cap = cv2.VideoCapture(0)
while(cap.isOpened()):
    ret, frame = cap.read()
    if ret==True:
        
        frame = readImage(frame)
        cv2.imshow('frame',frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break
cap.release()
out.release()
cv2.destroyAllWindows()

