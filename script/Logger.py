import script.Globals as Globals
import datetime


class Logger:
    def __init__(self):
        now = datetime.datetime.now()
        datetimeNow = now.strftime("%Y-%m-%d_%H-%M-%S")
        self.errorFile = "log/error_" + datetimeNow + ".txt"
    
    def log(self, *args):
        now = datetime.datetime.now()
        datetimeNow = now.strftime("%Y-%m-%d_%H-%M-%S")
        
        text = ""
        for arg in args:
            text += str(arg) + " "
        
        with open(self.errorFile, "a+") as errorFile:
            errorFile.write("\n\n" + datetimeNow + "\n" + text)


logger = Logger()
