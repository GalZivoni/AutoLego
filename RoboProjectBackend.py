import os
import cv2,redis
import numpy as np,random
import time #using time.sleep with DELAY time avoiding over usage of nxt controller





class CompScreen():

    def __init__(self,computer_name):
        self.redis_address='192.168.1.101'
        self.r=redis.StrictRedis(self.redis_address,6379,0,decode_responses=True,charset='utf-8')
        self.prev_redis_read=None
        self.curr_redis_read=None
        self.comp=computer_name


    def read_from_redis(self):
        if self.r:
            print("connected to redis")
        # Reading relevant keys from redis
        print(self.r.keys('*:segaction'))
        keys_lst=self.r.keys('*:segaction')
        print(keys_lst)
        # If the list is not empty
        if keys_lst:
            for key in keys_lst:
                # If the key is for the relevant computer
                if key.split(':')[0]==self.comp:
                    # Get the key value
                    action_value=self.r.get(key)
                    print(action_value)
                    # If the value we read isn't the same as the current value
                    if action_value!=self.curr_redis_read:
                        # Initiate previous value and current value
                        self.prev_redis_read=self.curr_redis_read
                        self.curr_redis_read=action_value
                        # Call the function to show the relevant image for the action on the computer screen
                        self.show_action(self.curr_redis_read)


    def show_action(self,action):
        print("enter")
        # Closing other windows if any were open
        cv2.destroyAllWindows()
        # Configuring full screen window to display the image
        cv2.namedWindow("image",cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("image",0,1)
        # Displaying the correct image based on the action input we have read from redis
        if action=="drive":
            cv2.imshow("image",cv2.imread("traffic light.jpg"))
            winkey=cv2.waitKey(1000)
            if winkey==27:   # ESC
                cv2.destroyAllWindows()
        elif action=="stop":
            cv2.imshow("image",cv2.imread("stop sign.jpg"))
            winkey = cv2.waitKey(1000)
            if winkey == 27:  # ESC
                cv2.destroyAllWindows()
        elif action == "turbo":
            cv2.imshow("image",cv2.imread("airplane.jpg"))
            winkey = cv2.waitKey(1000)
            if winkey == 27:  # ESC
                cv2.destroyAllWindows()
        elif action == "circle":
            cv2.imshow("image",cv2.imread("donut.jpg"))
            winkey = cv2.waitKey(1000)
            if winkey == 27:  # ESC
                cv2.destroyAllWindows()
        elif action == "music":
            cv2.imshow("image",cv2.imread("wineglass.jpg"))
            winkey = cv2.waitKey(1000)
            if winkey == 27:  # ESC
                cv2.destroyAllWindows()


computer=CompScreen("comp1")
while True:
    computer.read_from_redis()
