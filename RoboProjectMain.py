
import sys
import redis
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty

class Mimshak(BoxLayout):
    'Read color and write direction'
    #Get IP address and color objects as class members from kv file gui
    ip=ObjectProperty()
    color=ObjectProperty()

    # def __init__(self,redis_address, robot_name, **kwargs):
    def __init__(self ,r=None,**kwargs):
        super().__init__(**kwargs)
        'Method that runs after pushing start button'
        #Connect to redis getting ip from gui
        self.r=r


    def redis_address(self):
        self.r=redis.StrictRedis(str(self.ip.text),6379,0,decode_responses=True,charset='utf-8')
        if self.r:
            print("Connected to redis")




    def choosecomp(self,comp,redis_object):
        'Method that open new screen'
        self.clear_widgets()
        if comp=="comp1":
            self.add_widget(Comp1(redis_object))
        elif comp=="comp2":
            self.add_widget(Comp2(redis_object))
        elif comp=="comp3":
            self.add_widget(Comp3(redis_object))







class Comp1(BoxLayout):
    'Read color and write direction'
    #Get IP address and color objects as class members from kv file gui
    computer1=ObjectProperty()

    def __init__(self, redis_object,**kwargs):
        super().__init__(**kwargs)
        self.comp_name = "comp1"
        self.r=redis_object

    def main_screen(self):
        self.clear_widgets()
        self.add_widget(Mimshak(self.r))

    def write_to_redis(self,comp,action):
        self.r.set(f"{comp}:segaction",action)


    def delete_keys(self):
        keys_to_delete=self.r.keys("*:segaction")
        for key in keys_to_delete:
            self.r.delete(key)


class Comp2(BoxLayout):
    'Read color and write direction'
    #Get IP address and color objects as class members from kv file gui
    computer1=ObjectProperty()

    def __init__(self,redis_object, **kwargs):
        super().__init__(**kwargs)
        self.comp_name = "comp2"
        self.r=redis_object


    def main_screen(self):
        self.clear_widgets()
        self.add_widget(Mimshak(self.r))

    def write_to_redis(self,comp,action):
        self.r.set(f"{comp}:segaction",action)



    def delete_keys(self):
        keys_to_delete=self.r.keys("*:segaction")
        for key in keys_to_delete:
            self.r.delete(key)


class Comp3(BoxLayout):
    'Read color and write direction'
    #Get IP address and color objects as class members from kv file gui
    computer1=ObjectProperty()

    def __init__(self, redis_object,**kwargs):
        super().__init__(**kwargs)
        self.comp_name="comp3"
        self.r=redis_object

    def main_screen(self):
        self.clear_widgets()
        self.add_widget(Mimshak(self.r))

    def write_to_redis(self,comp,action):
        self.r.set(f"{comp}:segaction",action)

    def delete_keys(self):
        keys_to_delete=self.r.keys("*:segaction")
        for key in keys_to_delete:
            self.r.delete(key)


class Kivy4moodleApp(App):
    pass

if __name__ == '__main__':
    Kivy4moodleApp().run()
