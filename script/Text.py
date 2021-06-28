import script.Globals as Globals
import os
import sys


class Text:
    def __init__(self):
        self.color = True
        self.colors = {
            "black": "232",
            "dark gray": "236",
            "gray": "242",
            "lightish gray": "247",
            "light gray": "250",
            "white": "255",
            "light red": "009",
            "lightish red": "198",
            "red": "196",
            "dark red": "088",
            "light orange": "215",
            "orange": "208",
            "yellow": "190",
            "light green": "077",
            "lightish green": "076",
            "dark green": "022",
            "green": "010",
            "light blue": "039",
            "blue": "004",
            "dark blue": "018",
            "very dark blue": "017",
            "light purple": "135",
            "purple": "128",
            "brown": "094",
            "option": "231"
        }
        
        self.hp = self.c("red") + "♥"
        self.mp = self.c("blue") + "♦"
        self.xp = self.c("green") + "•"
        self.gp = self.c("yellow") + "●"
        
        for color in self.colors:
            setattr(self, color.replace(" ", ""), self.c(color))
        
        self.reset = "\x1b[0m" if Globals.ansiEnabled else ""
        
        self.clearCommand = "cls" if Globals.system == "Windows" else "clear"
    
    # - Ansi - #
    def c(self, color, back=False, code=False):
        if Globals.ansiEnabled and self.color:
            ansi = "\x1b[48;5;" if back else "\x1b[38;5;"
            return f'{ansi}{color if code else self.colors[color]}m'
        else:
            return ""
    
    @staticmethod
    def set_cursor_visible(visible):
        if Globals.ansiEnabled:
            print("\x1b[?25h" if visible else "\x1b[?25l", end="")
            sys.stdout.flush()

    @staticmethod
    def resizeConsole(rows, cols):
        if Globals.ansiEnabled:
            print(f'\x1b[8;{cols};{rows}t')
    
    def clear(self):
        os.system(self.clearCommand)
        self.set_cursor_visible(False)
    
    # - Returning - #
    
    @staticmethod
    def title(name, level):
        return f'{name} [Lvl {level}]'
    
    def bar(self, value, maximum, color, length=32, number=False):
        if value < 0:
            value = 0
        filledLength = round(value / maximum * length)
        
        filledText = self.c(color) + "#" * filledLength
        backText = self.gray + "-" * (length - filledLength)
        number = f' {value}/{maximum}' if number else ""
        
        return filledText + backText + self.reset + number
    
    @staticmethod
    def numeral(number):
        numberToNumeral = {
            1: "I",
            2: "II",
            3: "III",
            4: "IV",
            5: "V",
            6: "VI",
            7: "VII",
            8: "VIII",
            9: "IX",
            10: "X"
        }
        
        if number in numberToNumeral:
            return numberToNumeral[number]
        else:
            return str(number)


text = Text()
