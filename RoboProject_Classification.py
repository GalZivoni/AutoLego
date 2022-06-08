
import os
import urllib.request
# import face_recognition
import cvlib as cv
import cv2
import numpy as np,random
import redis
import time #using time.sleep with DELAY time avoiding over usage of nxt controller



class Auto():

    '''
    Class for autonomous vehicle.
    '''
    def __init__(self):
        '''
        Setup.
        '''
        # Connect to redis
        # Establish redis client connection
        self.r = redis.StrictRedis('192.168.1.101', 6379, 0, decode_responses=True, charset='utf-8')
        # Get brick name
        # Set initial values for x,y class variables.
        self.x ,self.y = -1,-1
        # Set url for the shot.jpg android snapshot.
        self.url = "http://192.168.1.100:8080/shot.jpg"
        self.labels_list=["stop sign","traffic light","airplane","donut","wine glass"]
        
    def classify_action(self,label):
        # Classifing actions for redis writing
        if label=="traffic light":
            return "drive"
        elif label=="stop sign":
            return "stop"
        elif label=="airplane":
            return "turbo"
        elif label=="donut":
            return "circle"
        elif label=="wine glass":
            return "music"


    def get_img(self):

        '''
        Get image from tablet.
        :return: Decoded image (BGR) and RGB image.
        '''
        # Send request to url.
        imgresp = urllib.request.urlopen(self.url)
#         # Read image as bytearray
        imgnp = np.array(bytearray(imgresp.read()), dtype=np.uint8)
#         # Decode image.
        img = cv2.imdecode(imgnp, -1)
#         # Change image from bgr to rgb
        img2 = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        # Return
        return img,img2
#         return  video_capture.read()


    


    def track_object(self):

        # Infinite loop
        while True:
            # Get bgr image and rgb image from self.get_img()
            self.rgb,self.decode_bgr= self.get_img()
            # Resize image box
            self.rgb2=cv2.resize(self.rgb, (0, 0), fx=0.5, fy=0.5)
            # Find bbox, labels, conf from cv.detect_common_objects
            bbox,labels,conf=cv.detect_common_objects(self.rgb)
            # Printing labels for debugging
            print(labels)
            print(conf)
            # running on all labels to check if they fit the labels list set in init
            for indx in range(len(labels)):
                if labels[indx] in self.labels_list and conf[indx]>=0.5:
                    # Declaring the label as a variable
                    lab_var=labels[indx]
                    # Make random color
                    color = list(np.random.random(size=3) * 256)
                    # Declare x boundaries of bounding box
                    x_left,x_right=bbox[indx][0],bbox[indx][2]
                    # Draw rectangle
                    cv2.rectangle(self.rgb2, (x_left, bbox[indx][1]), (x_right,bbox[0][3]), color, 4)
                    # Put text
                    cv2.putText(self.rgb2,labels[indx],(x_left,bbox[indx][1]-10),cv2.FONT_HERSHEY_SIMPLEX,1,color)
                    # Classify action
                    action_classified=self.classify_action(lab_var)
                    # Print classification for debugging
                    print(action_classified)
                    # Write to redis
                    self.r.set(f"segtodo",action_classified)
                    # Break from loop
                    break


            # Show picture
            cv2.imshow('img', self.rgb2)
            # Waitkey
            w = cv2.waitKey(10) & 0xFF
            # If user pressed q
            if w == ord('q'):
                self.exit()
                # Break
                break

    def exit(self):
        '''
        Exit after user press q or touch sensor was pressed
        :return:
        '''
        # Destroy windows.
        cv2.destroyAllWindows()
        



car=Auto()
car.track_object()






