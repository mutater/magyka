from script.Globals import *
import os
import playsound
import random
import threading


class Sound:
    def __init__(self):
        self.sounds = {}
    
        for file in os.listdir("sound"):
            if file.endswith(".mp3"):
                self.sounds.update({file.split(".")[0]: "sound/" + file})
    
    def play_sound(self, sound):
        if type(sound) is list:
            sound = self.sounds[sound[random.randint(0, len(sound) - 1)]]
        else:
            sound = self.sounds[sound]
        t = threading.Thread(target=playsound.playsound, args=(sound,))
        t.start()


sound = Sound()
    
    