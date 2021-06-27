from script.Control import control
import script.Globals as Globals
from script.Text import text
import os, sys, time

class Printing:
    def __init__(self):
        pass
    
    
    def header(self, text):
        print("\n -= " + text + " =-")
    
    
    def options(self, names):
        if len(names) > 0: print("")
        
        for i in range(len(names)):
            print(f' {text.c("option") + text.c("dark gray", True)}[{names[i][11 if ";" in names[i] else 0]}]{text.reset} {names[i]}')
            if i < len(names)-1:
                print(f' {text.c("option") + text.c("dark gray", True)} |{text.reset}')
        
        print(text.reset, end="")
    
    
    def write(self, text, speed):
        i = 0
        delay = speed
        while i < len(text):
            if text[i:i+2] == "0m":
                print(text.reset, end="")
                i += 1
            elif text[i:i+5] == "38;5;":
                print("\x1b[" + text[i:i+10], end="")
                i += 9
            elif text[i] == "#":
                control.press_enter()
                delay = speed
            elif text[i] == "<":
                clear()
                delay = speed
            else:
                print(text[i], end="")
            
            time.sleep(delay)
            
            if control.get_key() == "enter":
                delay = 0
            
            sys.stdout.flush()
            i += 1
        
        print("")

printing = Printing()
