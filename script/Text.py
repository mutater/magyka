import script.Globals as Globals
from script.Mapper import mapper
import os
import sys
import time


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
            "option": "231",
            "terminal": "000"
        }
        
        self.rarityColors = {
            "garbage": "light red",
            "common": "lightish gray",
            "uncommon": "lightish green",
            "rare": "light blue",
            "epic": "light purple",
            "legendary": "light orange",
            "mythical": "lightish red"
        }
        
        self.hp = self.c("red") + "♥"
        self.mp = self.c("blue") + "♦"
        self.xp = self.c("green") + "•"
        self.gp = self.c("yellow") + "●"
        
        for color in self.colors:
            setattr(self, color.replace(" ", ""), self.c(color))
        
        self.reset = "\x1b[0m" if Globals.ansiEnabled else ""
        
        os.system("cls" if Globals.system == "Windows" else "clear")
        self.set_cursor_visible(False)
        
        animations = []
    
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
        if Globals.ansiEnabled:
            self.fill_screen("")
            self.move_cursor(1, 1)
    
    def move_cursor(self, row, col):
        if Globals.ansiEnabled:
            print(f'\x1b[{row};{col}H', end="")
        else:
            print("\n You shouldn't be seeing this. (text.move_cursor)")
    
    def slide_cursor(self, row=0, col=0):
        if Globals.ansiEnabled:
            if row:
                print(f'\x1b[{row}B', end="")
            if col:
                print(f'\x1b[{col}C', end="")
    
    # - Printing - #
    def header(self, string, row=3, col=85):
        self.print_at_loc(("-= " + string + " =-").center(32), row, col)
    
    def clear_header(self, row=3, col=85):
        self.print_at_loc(" "*32, row, col)
    
    def clear_description(self):
        self.print_at_loc((" "*36 + "\n") * 28, 2, 83)
    
    def options(self, names):
        if len(names) > 0:
            print("")
        
        for i in range(len(names)):
            self.slide_cursor(0, 3)
            print(f'{self.option + self.c("dark gray", True)}[{names[i][11 if ";" in names[i] else 0]}]{self.reset} {names[i]}')
            if i < len(names)-1:
                self.slide_cursor(0, 3)
                print(f'{self.option + self.c("dark gray", True)} | {self.reset}')
        
        print(self.reset, end="")
    
    def fill_screen(self, color):
        if color:
            print(self.c(color, back=True))
        else:
            print(self.reset)
        for i in range(os.get_terminal_size()[1]):
            self.move_cursor(i + 1, 0)
            print(" "*os.get_terminal_size()[0], end="")
    
    def fill_rect(self, color, r, c, w, h):
        for i in range(h):
            self.move_cursor(i + r, c)
            if color:
                print(self.c(color, back=True) + " "*w, end="")
            else:
                print(self.reset + " "*w, end="")
    
    def print_at_loc(self, string, r, c):
        self.move_cursor(r, c)
        print(string, end="")
    
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
