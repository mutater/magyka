from script.Control import control
import script.Globals as Globals
from script.Text import text
import sys
import time


class Printing:
    def __init__(self):
        pass
    
    @staticmethod
    def header(string):
        print("\n -= " + string + " =-")
    
    @staticmethod
    def options(names):
        if len(names) > 0:
            print("")
        
        for i in range(len(names)):
            print(f' {text.c("option") + text.c("dark gray", True)}[{names[i][11 if ";" in names[i] else 0]}]{text.reset} {names[i]}')
            if i < len(names)-1:
                print(f' {text.c("option") + text.c("dark gray", True)} |{text.reset}')
        
        print(text.reset, end="")
    
    @staticmethod
    def write(string, speed):
        i = 0
        delay = speed
        while i < len(string):
            if string[i:i+2] == "0m":
                print(text.reset, end="")
                i += 1
            elif string[i:i+5] == "38;5;":
                print("\x1b[" + string[i:i+10], end="")
                i += 9
            elif string[i] == "#":
                control.press_enter()
                delay = speed
            elif string[i] == "<":
                text.clear()
                delay = speed
            else:
                print(string[i], end="")
            
            time.sleep(delay)
            
            if control.get_key() == "enter":
                delay = 0
            
            sys.stdout.flush()
            i += 1
        
        print("")


printing = Printing()
