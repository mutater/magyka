import script.Globals as Globals
import os
import sys


class Text:
    """
    Contains ANSI printing methods and ANSI colors.
    """
    def __init__(self):
        """
        Initializes the class and creates class variables based on the self.colors dict.
        """

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
        self.underline = "\x1b[4m" if Globals.ansiEnabled else ""
        
        os.system("cls" if Globals.system == "Windows" else "clear")
        self.set_cursor_visible(False)
        
        animations = []

    def c(self, color, back=False):
        """
        Returns an ANSI color code from a color name provided.

        Args:
            color:
                String name of the color.
            back:
                Bool whether color be background or not.

        Returns:
            String containing ANSI color.
        """

        if Globals.ansiEnabled and self.color:
            ansi = "\x1b[48;5;" if back else "\x1b[38;5;"
            return f'{ansi}{self.colors[color]}m'
        else:
            return ""
    
    def cc(self, color, back=False):
        """
        Returns an ANSI color code from an ANSI color code provided.

        Args:
            color:
                String or Integer ANSI color code.
            back:
                Bool whether color be background or not.

        Returns:
            String containing ANSI color.
        """

        if Globals.ansiEnabled and self.color:
            ansi = "\x1b[48;5;" if back else "\x1b[38;5;"
            return f'{ansi}{color}m'
        else:
            return ""
    
    def rgb(self, color, back=False):
        """
        Returns an ANSI color code from an RGB color provided.

        Args:
            color:
                String RGB color in the form "r;g;b".
            back:
                Bool whether color be background or not.

        Returns:
            String containing ANSI color.
        """

        if Globals.ansiEnabled and self.color:
            if color == "255;0;255":
                color = "12;12;12"
            ansi = "\x1b[48;2;" if back else "\x1b[38;2;"
            return f'{ansi}{color}m'
        else:
            return ""
    
    @staticmethod
    def set_cursor_visible(visible):
        if Globals.ansiEnabled:
            print("\x1b[?25h" if visible else "\x1b[?25l", end="")
            sys.stdout.flush()

    @staticmethod
    def resize_console(rows, cols):
        """
        Resizes the terminal. Doesn't really work outside of Windows.

        Args:
            rows:
                Integer height of console in characters.
            cols:
                Integer width of console in characters.
        """

        if Globals.ansiEnabled:
            print(f'\x1b[8;{cols};{rows}t')
    
    def clear(self):
        """
        Clears the screen.
        """

        if Globals.ansiEnabled:
            self.fill_screen("")
            self.move_cursor(1, 1)

    @staticmethod
    def move_cursor(row, col):
        """
        Moves the cursor to a specific point on the terminal.

        Args:
            row:
                Integer y location the cursor is moved to, in characters.
            col:
                Integer x location he cursor is moved to, in characters.
        """

        if Globals.ansiEnabled:
            print(f'\x1b[{row};{col}H', end="")
        else:
            print("\n You shouldn't be seeing this. (text.move_cursor)")

    @staticmethod
    def slide_cursor(row=0, col=0):
        """
        Slides the cursor a specific distance on the terminal.

        Args:
            row:
                Integer y distance the cursor is moved, in characters.
            col:
                Integer x distance the cursor is moved, in characters.
        """

        if Globals.ansiEnabled:
            if row:
                print(f'\x1b[{row}B', end="")
            if col:
                print(f'\x1b[{col}C', end="")

    def header(self, string, row=3, col=85, w=32):
        """
        Prints a header in the form "-= STRING =-" at a specific location.

        Args:
            string:
                String in the header.
            row:
                Integer y location of the leftmost character of the header. Default is 3.
            col:
                Integer x location of the leftmost character of the header. Default is 85.
            w:
                Integer that centers the header in the spaces around it. Default is 32.
        """

        self.move_cursor(row, col)
        print(("-= " + string + " =-").center(w))
    
    def clear_header(self, row=3, col=85):
        """
        Clears the header.

        Args:
            row:
                Integer y location of the leftmost character of the header. Default is 3.
            col:
                Integer x location of the leftmost character of the header. Default is 85.
        """

        print(self.reset, end="")
        self.move_cursor(row, col)
        print(" "*32)
    
    def clear_main(self):
        """
        Clears the main box of the screen.
        """

        print(self.reset, end="")
        for i in range(28):
            self.move_cursor(2 + i, 3)
            print(" "*78)
    
    def clear_main_small(self):
        """
        Clears the main box of the screen, when it's small.
        """

        print(self.reset, end="")
        for i in range(28):
            self.move_cursor(2 + i, 3)
            print(" "*38)
    
    def clear_description(self):
        """
        Clears the description.
        """

        print(self.reset, end="")
        for i in range(28):
            self.move_cursor(2 + i, 83)
            print(" "*36)
    
    def options(self, names, space=3):
        """
        Prints a list of options.

        Args:
            names:
                List of strings. Accepts ANSI color strings.
            space:
                Integer padding from the left edge of the screen. Defaults to 3.

        Returns:
            String of option characters.
        """

        options = ""

        if len(names) > 0:
            print("")
        
        for i in range(len(names)):
            character = names[i][11 if ";" in names[i] else 0]
            options += character.lower()

            self.slide_cursor(0, space)
            print(f'{self.option + self.c("dark gray", True)}[{character}]{self.reset} {names[i]}')
            if i < len(names)-1:
                self.slide_cursor(0, space)
                print(f'{self.option + self.c("dark gray", True)} | {self.reset}')
        
        print(self.reset, end="")

        return options
    
    def fill_screen(self, color):
        """
        Fills the screen with a color.

        Args:
            color:
                String color.
        """

        if color:
            print(self.c(color, back=True))
        else:
            print(self.reset)

        for i in range(os.get_terminal_size()[1]):
            self.move_cursor(i + 1, 0)
            print(" "*os.get_terminal_size()[0], end="")
        sys.stdout.flush()
    
    def print_at_description(self, text, r=3, c=84):
        """
        Prints text in the description.

        Args:
            text:
                String to be printed.
            r:
                Integer y location of the top left corner of text. Default is 3.
            c:
                Integer x location of the top left corner of text. Default is 84.
        """

        for i in range(len(text)):
            self.move_cursor(r + i, c)
            print(text[i].strip())

    @staticmethod
    def title(name, level, playerClass=""):
        return f'{name} [Lvl {level}{" " + playerClass if playerClass else ""}]'
    
    def bar(self, value, maximum, color, length=32, number=False):
        """
        Prints a colored bar.

        Args:
            value:
                Integer value to be divided by maximum.
            maximum:
                Integer using value to calculate percentage of the bar to be filled.
            color:
                String color of the bar.
            length:
                Integer length of the bar, in characters.
            number:
                Boolean; if True, shows the value + "/" + number after the bar. Default is False.

        Returns:
            String containing ANSI color.
        """
        if value < 0:
            value = 0
        filledLength = round(value / maximum * length)
        
        filledText = self.c(color) + self.c("dark " + color, back=True) + "#" * filledLength
        backText = self.gray + self.c("dark gray", back=True) + "-" * (length - filledLength)
        number = f' {value}/{maximum}' if number else ""
        
        return self.underline + filledText + backText + self.reset + number
    
    @staticmethod
    def numeral(number):
        """
        Turns a number into a Roman numeral.

        Args:
            number:
                Integer 1-10.

        Returns:
            String.
        """

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
