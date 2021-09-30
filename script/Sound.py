from script.Settings import settings
import os
import playsound
import random
import threading


class Sound:
    """
    Plays sounds in a different thread.
    """
    def __init__(self):
        """
        Initializes the class and loads all game audio.
        """

        self.sounds = {}
    
        for file in os.listdir("sound"):
            if file.endswith(".mp3"):
                self.sounds.update({file.split(".")[0]: "sound/" + file})
    
    def play_sound(self, name):
        """
        Plays a loaded sound or sounds.

        Args:
            name:
                String name of the sound in files without the extension.

                If provided with a list of sounds, a random sound from the list will be chosen.
        """

        if settings.sound:
            if type(name) is list:
                name = self.sounds[name[random.randint(0, len(name) - 1)]]
            else:
                name = self.sounds[name]

            t = threading.Thread(target=playsound.playsound, args=(name,))
            t.start()


sound = Sound()
    
    