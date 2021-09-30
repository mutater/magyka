import datetime


class Logger:
    """
    Class for logging to a log file.
    """

    def __init__(self):
        """
        Initializes the class.
        """

        now = datetime.datetime.now()
        datetimeNow = now.strftime("%Y-%m-%d_%H-%M-%S")
        self.errorFile = "log/error_" + datetimeNow + ".txt"
    
    def log(self, *args):
        """
        Logs to the log file.

        Parameters:
            *args:
                Objects to be logged.
        """

        now = datetime.datetime.now()
        datetimeNow = now.strftime("%Y-%m-%d_%H-%M-%S")
        
        text = ""
        for arg in args:
            text += str(arg) + " "
        
        with open(self.errorFile, "a+") as errorFile:
            errorFile.write("\n\n" + datetimeNow + "\n" + text)


logger = Logger()
