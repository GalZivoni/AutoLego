
import nxt.locator,nxt.sensor,nxt.motor
import redis #import client for redis server
import time #using time.sleep with DELAY time avoiding over usage of nxt controller
POWER = 20
TURN = 25
TURN_DELAY = 0.3
DELAY = 1
















#Name of class Mimshak changed to Backend
class Backend:
    #Change start method to class constructor _init_
    def __init__(self):
        'The Constructor'
        #Print date and time
        print(time.asctime())
        # Get brick name using raw_input function from user
        self.brickName=raw_input('Type your brick name\n')
        # Get handle for the brick using nxt.locator.find_one_brick same as original file
        self.brick=nxt.locator.find_one_brick(name=self.brickName)
        # Define two motors same as original file
        self.right = nxt.Motor(self.brick,nxt.motor.PORT_A)
        self.left = nxt.Motor(self.brick, nxt.motor.PORT_C)
        # Define touch sensor
        self.touch=nxt.sensor.Touch(self.brick,nxt.sensor.PORT_2)
        # Initiating color sensor
        self.light=nxt.sensor.Light(self.brick,nxt.sensor.PORT_3)
        self.light.set_input_mode(nxt.sensor.Type.LIGHT_ACTIVE,nxt.sensor.Mode.RAW)
        # First value is white to be used as a flag
        self.color="white"
        # Establish redis client connection
        self.redis_comp=redis.StrictRedis('192.168.1.101',6379,0, decode_responses=True,charset='utf-8')
        # Writing brick name to redis
        self.redis_comp.set("bricknameseg",self.brickName)
        # Setting the robot to stop at first
        self.redis_comp.set(self.brickName+':kivun','Stop')
        # Setting the robot to start at auto drive
        self.redis_comp.set(self.brickName +":driveoption","auto")
        # Setting the robot auto direction to forward
        self.redis_comp.set(self.brickName+':autokivun','Forward')
        # Setting an inital value to manual direction, automated direction,power and flag
        self.kivun='Start'
        self.power=POWER
        self.flag=True
        self.auto_kivun="Start"
        
        # Initating first redis read flag to know if the robot should drive manualy or automated
        self.first_read=True
        # Initating a counter to number of black reads (at 4 it should drive on reverse and be 0 again)
        self.black_reads_number=0
        # Initating a loop variable to break from color looping later in the code
        self.color_loop=True
        # Initiating available actions
        self.known_actions=["drive","stop","turbo","circle","music"]
        #Initiating light limit
        self.saf=400
        self.original_light_val=0
        # Initating a reverse counter
        self.reverse_count=0
        # Deleting registries if they exist on redis
        if self.redis_comp.get("segtodo"):
            self.redis_comp.delete("segtodo")



    def stop(self):
        'Stop method that stops both engines'
        self.right.brake()
        self.left.brake()

    def auto_drive(self):
        #### We can change to read if manual is activated and then switch if we want to. For now it runs infinitly
        print("Starting auto drive")
        while True:
        # Read the direction
            self.color_loop=True
            self.auto_kivun = self.redis_comp.get(self.brickName + ':autokivun')
            print(self.auto_kivun)

            # If the direction is forward
            if self.auto_kivun=="Forward":
                print("Driving Forward from auto drive")
                self.forward_auto_drive()

                
            elif self.auto_kivun=="Reverse":
                print("Driving Backwards from auto drive")
                self.reverse_auto_drive()
                           
                          
                                 
    
    def forward_auto_drive(self):
        self.original_light_val=self.light.get_sample()
        print(self.original_light_val)
        # If we don't encounter a black color
        while self.color=="white" and self.color_loop:
            # Drive forward
            self.left.run(self.power)
            self.right.run(self.power)
            # sample light
            light_val=self.light.get_sample()
            print(light_val)

            # If the light is black
            if light_val>=545:
                self.saf=light_val
                print("Stopping at black line")

                # Stop
                self.stop()

                # Set color to black and raise counter by 1
                self.color=="black"
                self.black_reads_number+=1



                # If it is the 4th time (the robot has reached the end)
                if self.black_reads_number==4:

                    # Set the robot to drive in reverse
                    self.redis_comp.set(self.brickName +":autokivun","Reverse")

                    # Initiate new black reads counter
                    self.black_reads_number=0

                    # Reset the color
                    self.color="white"

                    # Drive away from the black color
                    self.left.run(-self.power)
                    self.right.run(-self.power)
                    self.brick.play_tone(500,150)
                    time.sleep(DELAY)

                    # Return to the main loop
                    return


                # If it is not the 4th time (the robot hasn't reached the end)
                else:
                    # Wait for action to be written and read from redis
                    while True:

                        # Read the value from redis
                        automated_action_read=self.redis_comp.get("segtodo")
                        print(automated_action_read)
                        # If the action is in the list of known actions
                        if automated_action_read in self.known_actions:
                            self.play_detected()
                            # Classify the action,delete the action from reids and break from the loop
                            self.action_classifier(automated_action_read,"Forward")
                            if self.redis_comp.get("segtodo"):
                                self.redis_comp.delete("segtodo")
                            # time.sleep(DELAY)
                            # Set the color to white so we can drive again - maybe we need to define it to go forward/backwards untill a white light is met
                            self.color="white"
                            # Exit from outside loop
                            self.color_loop=False
                            break
                            
    def reverse_auto_drive(self):
        self.reverse_count=0
        # If we don't encounter a black color
        self.original_light_val=self.light.get_sample()
        print(self.original_light_val)
        print(self.color,self.color_loop)
        while self.color=="white" and self.color_loop:
            # Drive forward
            self.left.run(-self.power)
            self.right.run(-self.power)
            self.reverse_count += 1
            if self.reverse_count%10==0:
                self.brick.play_tone(500,250)
            # sample light
            light_val=self.light.get_sample()

            # If the light is black
            if light_val>=545:
                self.saf=light_val
                # Stop
                self.stop()

                # Set color to black and raise counter by 1
                self.color=="black"
                self.black_reads_number+=1



                # If it is the 4th time (the robot has reached the end)
                if self.black_reads_number==4:

                    # Set the robot to drive forward
                    self.redis_comp.set(self.brickName + ":autokivun","Forward")

                    # Initiate new black reads counter
                    self.black_reads_number=0

                    # Reset the color
                    self.color="white"

                    # Drive away from the black color
                    self.left.run(self.power)
                    self.right.run(self.power)
                    time.sleep(DELAY)

                    # Return to the main loop
                    return


                # If it is not the 4th time (the robot hasn't reached the end)
                else:
                    #Wait for action to be written and read from redis
                    while True:

                        # Read the value from redis
                        automated_action_read=self.redis_comp.get("segtodo")
                        # If the action is in the list of known actions
                        if automated_action_read in self.known_actions:
                            self.play_detected()
                            # Classify the action,delete the action from reids and break from the loop
                            self.action_classifier(automated_action_read,"Backward")
                            if self.redis_comp.get("segtodo"):
                                self.redis_comp.delete("segtodo")
                            # Set the color to white so we can drive again
                            self.color="white"
                            # Exit from outside loop
                            self.color_loop=False
                            break


    def action_classifier(self,action_value,mode):
        
        # If the action is drive
        if action_value=="drive":
            # If we go forward
            if mode=="Forward":
                # Print for debugging, and drive forward
                print("Detected action drive, driving forward")
                for i in range(2):
                    self.left.run(self.power)
                    self.right.run(self.power)
                    time.sleep(DELAY)
            
            # If we're in reverse mode
            elif mode=="Backward":
                # Print for debugging, and drive backwards
                print("Detected action drive, driving backwards")
                for i in range(2):
                    self.left.run(-self.power)
                    self.right.run(-self.power)
                    time.sleep(DELAY)
                

        elif action_value=="stop":
            # Print for debugging, and stop
            print("Detected action stop, stopping untill action is drive")
            while True:
                # Read from redis to wait for forward cue
                stop_action_value=self.redis_comp.get("segtodo")
                # If the action is drive
                if stop_action_value=="drive":
                    if mode=="Forward":
                        # Print for debugging, and drive forward
                        print("Detected action drive, driving forward")
                        for i in range(1):
                            self.left.run(self.power)
                            self.right.run(self.power)
                            time.sleep(DELAY)
                        break
                    
                    # If we're in reverse mode    
                    elif mode=="Backward":
                        # Print for debugging, and drive backwards
                        print("Detected action drive, driving backwards")
                        for i in range(1):
                            self.left.run(-self.power)
                            self.right.run(-self.power)
                            time.sleep(DELAY)
                        break
                        
        elif action_value=="turbo":
            # If we go forward
            if mode=="Forward":
                # Print for debugging, and drive fast
                print("Detected action turbo, driving forward fast")
                for i in range(3):
                    self.left.run(self.power*1.5)
                    self.right.run(self.power*1.5)
                    time.sleep(DELAY)
            
            # If we're in reverse mode
            elif mode=="Backward":
                # Print for debugging, and drive fast
                print("Detected action turbo, driving backward fast")
                for i in range(3):
                    self.left.run(-self.power*1.5)
                    self.right.run(-self.power*1.5)
                    time.sleep(DELAY)

        elif action_value=="circle":
            # Print for debugging, and perform a circle
            print("Detected action circle, doing a circle")
            # Doing 7 turns to the right to do a circle
            for num_of_turns in range(25):
                self.left.run(-TURN)
                self.right.run(TURN)
                time.sleep(TURN_DELAY)
            
            # Getting away from black line
            
            # If we go forward
            if mode=="Forward":
                # Print for debugging, and drive forward
                print("Getting away from black line , driving forward")
                for i in range(2):
                    self.left.run(self.power)
                    self.right.run(self.power)
                    time.sleep(DELAY)
            
            # If we're in reverse mode
            elif mode=="Backward":
                # Print for debugging, and drive backwards
                print("Getting away from black line , driving backwards")
                for i in range(2):
                    self.left.run(-self.power)
                    self.right.run(-self.power)
                    time.sleep(DELAY)
                
               
        elif action_value=="music":
            # Print for debugging, and play music
            print("Detected action music, playing music")
            # Play music
            self.play_music()
            # Drive forward to get away from black line
            if self.redis_comp.get("segtodo"):
                self.redis_comp.delete("segtodo")
            
            # If we go forward
            if mode=="Forward":
                # Print for debugging, and drive forward
                print("Getting away from black line , driving forward")
                for i in range(2):
                    self.left.run(self.power)
                    self.right.run(self.power)
                    time.sleep(DELAY)
            
            # If we're in reverse mode
            elif mode=="Backward":
                # Print for debugging, and drive backwards
                print("Getting away from black line , driving backwards")
                for i in range(2):
                    self.left.run(-self.power)
                    self.right.run(-self.power)
                    time.sleep(DELAY)

            
            
            
                
    
    def play_music(self):
        notes = {'NOTE_B0': 31, 'NOTE_C1': 33, 'NOTE_CS1': 35
            , 'NOTE_D1': 37, 'NOTE_DS1': 39, 'NOTE_E1': 41, 'NOTE_F1': 44, 'NOTE_FS1': 46, 'NOTE_G1': 49,
                 'NOTE_GS1': 52, 'NOTE_A1': 55
            , 'NOTE_AS1': 58, 'NOTE_B1': 62, 'NOTE_C2': 65, 'NOTE_CS2': 69, 'NOTE_D2': 73, 'NOTE_DS2': 78, 'NOTE_E2': 82
            , 'NOTE_F2': 87, 'NOTE_FS2': 93, 'NOTE_G2': 98, 'NOTE_GS2': 104, 'NOTE_A2': 110, 'NOTE_AS2': 117,
                 'NOTE_B2': 123, 'NOTE_C3': 131
            , 'NOTE_CS3': 139, 'NOTE_D3': 147, 'NOTE_DS3': 156, 'NOTE_E3': 165, 'NOTE_F3': 175, 'NOTE_FS3': 185,
                 'NOTE_G3': 196, 'NOTE_GS3': 208
            , 'NOTE_A3': 220, 'NOTE_AS3': 233, 'NOTE_B3': 247, 'NOTE_C4': 262, 'NOTE_CS4': 277, 'NOTE_D4': 294,
                 'NOTE_DS4': 311
            , 'NOTE_E4': 330, 'NOTE_F4': 349, 'NOTE_FS4': 370, 'NOTE_G4': 392, 'NOTE_GS4': 415, 'NOTE_A4': 440,
                 'NOTE_AS4': 466,
                 'NOTE_B4': 494, 'NOTE_C5': 523, 'NOTE_CS5': 554, 'NOTE_D5': 587, 'NOTE_DS5': 622, 'NOTE_E5': 659,
                 'NOTE_F5': 698,
                 'NOTE_FS5': 740, 'NOTE_G5': 784, 'NOTE_GS5': 831, 'NOTE_A5': 880, 'NOTE_AS5': 932, 'NOTE_B5': 988,
                 'NOTE_C6': 1047,
                 'NOTE_CS6': 1109, 'NOTE_D6': 1175, 'NOTE_DS6': 1245, 'NOTE_E6': 1319, 'NOTE_F6': 1397,
                 'NOTE_FS6': 1480, 'NOTE_G6': 1568,
                 'NOTE_GS6': 1661, 'NOTE_A6': 1760, 'NOTE_AS6': 1865, 'NOTE_B6': 1976, 'NOTE_C7': 2093,
                 'NOTE_CS7': 2217, 'NOTE_D7': 2349,
                 'NOTE_DS7': 2489, 'NOTE_E7': 2637, 'NOTE_F7': 2794, 'NOTE_FS7': 2960, 'NOTE_G7': 3136,
                 'NOTE_GS7': 3322, 'NOTE_A7': 3520,
                 'NOTE_AS7': 3729, 'NOTE_B7': 3951, 'NOTE_C8': 4186, 'NOTE_CS8': 4435, 'NOTE_D8': 4699,
                 'NOTE_DS8': 4978}

        durations = [
            8, 8, 8, 4, 4, 4,
            4, 5, 8, 8, 8, 8,
            8, 8, 8, 4, 4, 4,
            4, 5, 8, 8, 8, 8]

        melody = [
            notes['NOTE_FS5'], notes['NOTE_FS5'], notes['NOTE_D5'], notes['NOTE_B4'], notes['NOTE_B4'],
            notes['NOTE_E5'],
            notes['NOTE_E5'], notes['NOTE_E5'], notes['NOTE_GS5'], notes['NOTE_GS5'], notes['NOTE_A5'],
            notes['NOTE_B5'],
            notes['NOTE_A5'], notes['NOTE_A5'], notes['NOTE_A5'], notes['NOTE_E5'], notes['NOTE_D5'], notes['NOTE_FS5'],
            notes['NOTE_FS5'], notes['NOTE_FS5'], notes['NOTE_E5'], notes['NOTE_E5'], notes['NOTE_FS5'],
            notes['NOTE_E5']
        ];

        for i in range(2):
            for note in range(len(melody)):
                duration = 1000 / durations[note]
                self.brick.play_tone_and_wait(int(melody[note]), int(duration))


        pass

    def play_detected(self):
        time.sleep(1)
        self.brick.play_tone_and_wait(int(1175), int(1000 / 8))
        time.sleep(0.1)
        self.brick.play_tone_and_wait(int(1175), int(1000 / 8))
        time.sleep(0.1)
        self.brick.play_tone_and_wait(int(1397), int(1000 / 32))
        time.sleep(0.1)
        self.brick.play_tone_and_wait(int(1175), int(1000 / 8))
        time.sleep(0.3)
        pass
    
    def read_from_redis(self):
        # If we read for the first time
        if self.first_read==True:
            while True:
                # Read the value option from redis
                redis_val=self.redis_comp.get(self.brickName+":driveoption")
                print(redis_val)
                # If the value is auto drive
                if redis_val=="auto":
                    # Set first read flag to false
                    self.first_read=False
                    # Initiate auto drive
                    self.auto_drive()
                    
                   


    def delete_registry(self):
        self.redis_comp.delete(self.brickName+":driveoption")
        # Setting the robot auto direction to forward
        self.redis_comp.delete(self.brickName + ':autokivun')
        if self.redis_comp.get("segtodo"):
            self.redis_comp.delete("segtodo")


if __name__=='__main__':
    # Instanciate class object
    backend=Backend()
    # Operate infinite loop
    # Read from redis
    backend.read_from_redis()
    backend.delete_registry()
