from script.Globals import *
import os
import playsound
import threading


class Sound:
    def __init__(self):
        self.sounds = {}
    
        for file in os.listdir("sound"):
            if file.endswith(".mp3"):
                self.sounds.update({file.split(".")[0]: "sound/" + file})
    
    def play_sound(self, sound):
        t = threading.Thread(target=playsound.playsound, args=(self.sounds[sound],))
        t.start()


sound = Sound()
    
    