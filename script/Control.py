import os
import re
import script.Globals as Globals
import sys
import time
from script.Logger import logger
from script.Sound import sound
from script.Text import text

if Globals.system == "Windows":
    import msvcrt
else:
    import tty
    import termios
    import select


class Control:
    """
    Manages keypress input by the player.
    """

    def __init__(self):
        """
        Initializes the class.
        """
        if not Globals.system == "Windows":
            self.orig_settings = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin)
        
        self.lastCommand = ""

    @staticmethod
    def get_key():
        """
        Gets the most recent keypress, if available, and returns it.

        Returns:
            String name of key pressed.
        """

        # Get the key
        key = ""
        if Globals.system == "Windows":
            if msvcrt.kbhit():
                key = msvcrt.getch()
                try:
                    key = key.decode("utf-8")
                except UnicodeDecodeError:
                    if key == b'\xe0':
                        key = "\xe0"
                    else:
                        key = ""
        else:
            if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
                key = sys.stdin.read(1)[0]
        
        # Return the key
        if key == "\n" or key == "\r":
            return "enter"
        elif key == "\x1b":
            return "esc"
        elif key == " ":
            return "space"
        elif key == "\x08":
            return "backspace"
        elif key == "\x7f":
            return "ctrl backspace"
        elif key == "\xe0":
            try:
                key = msvcrt.getch().decode("utf-8")
            except UnicodeDecodeError:
                key = ""
            if key == "K":
                return "left"
            elif key == "M":
                return "right"
            elif key == "H":
                return "up"
            else:
                return "down"
        else:
            return key

    def reset_input_settings(self):
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.orig_settings)

    def wait_for_key(self, key):
        """
        Blocks the code until a specified keypress.

        Parameters:
            key:
                String name of the key.
        """

        while 1:
            time.sleep(0.05)
            if self.get_key() == key:
                break
    
    def time_keypress(self, timeout, key="space"):
        """
        Blocks the code until a specified keypress or timeout of length specified and returns the time taken.

        Parameters:
            timeout:
                Integer length of time in milliseconds before timeout.
            key:
                String name of key.

        Returns:
            Integer response time in milliseconds.
        """

        reactionTime = 0
        while 1:
            time.sleep(0.01)
            reactionTime += 0.01

            if self.get_key() == key:
                return round(reactionTime, 2) * 1000
            if round(reactionTime, 2) * 1000 >= timeout:
                return timeout + 1
    
    def press_enter(self):
        text.set_cursor_visible(False)
        text.move_cursor(text.pressEnterRow, text.pressEnterCol)
        print(f'{text.option}[Press Enter]{text.reset}')
        self.wait_for_key("enter")
    
    def get_input(self, mode="alphanumeric", back=True, showText=True, options=False, prompt="", silentOptions=""):
        textField = False

        if options:
            textField = False
        elif options == "":
            textField = False
        elif mode == "none":
            textField = False
        elif options != "":
            textField = True

        if textField:
            text.slide_cursor(1, 3)
            if mode == "command":
                print(f'{text.option}Console >| {text.reset}', end="")
            else:
                print(f'{text.option}> {text.reset}', end="")
            text.set_cursor_visible(True)
        else:
            helpText = ""
            
            if mode == "none":
                helpText = ""
            elif mode == "alphabetic":
                helpText = "- Press a letter"
            elif mode == "numeric":
                helpText = "- Press a number"
            elif mode == "alphanumeric" or mode == "optionumeric":
                helpText = "- Press a letter or number"
            
            if back and not mode == "none":
                helpText += ", or press ESC to go back."
            elif back and mode == "none":
                helpText += "Press ESC to go back."
            else:
                helpText += "."
            
            if showText:
                print("")
                text.slide_cursor(0, 3)
                print(helpText)
        
        a = prompt
        loc = len(prompt)
        if textField:
            print(a, end="")
        sys.stdout.flush()
        terminalSize = os.get_terminal_size()
        while 1:
            time.sleep(0.02)
            key = self.get_key()
            if not terminalSize == os.get_terminal_size():
                return "/C"

            # Looking for single character keys
            if len(key) == 1 and ((
                    mode in ("command", "all")
                    or (re.match("[0-9]", key) and mode in ("numeric", "optionumeric", "alphanumeric"))
                    or (re.match("[A-Za-z]", key) and mode in ("alphabetic", "optionumeric", "alphanumeric")))):
                if textField:
                    a = a[:loc] + key + a[loc:]
                    loc += 1
                    print(key + a[loc:], end="")
                    for i in range(len(a) - loc):
                        print("\b", end="")
                    sys.stdout.flush()
                elif key in options or key.lower() in options:
                    if key not in silentOptions:
                        sound.play_sound("select")
                    a = key
                    break
            # Adding a space
            if key == "space" and textField:
                a = a[:loc] + " " + a[loc:]
                loc += 1
                print(" " + a[loc:], end="")
                for i in range(len(a) - loc):
                    print("\b", end="")
                sys.stdout.flush()
            # Moving the cursor
            if key == "left" and loc > 0:
                loc -= 1
                sys.stdout.write("\b")
                sys.stdout.flush()
            if key == "right" and loc < len(a):
                loc += 1
                sys.stdout.write(a[loc-1])
                sys.stdout.flush()
            # Backspacing
            if key == "backspace":
                if len(a) > 0:
                    sys.stdout.write("\b" + a[loc:] + " ")
                    for i in range(len(a) - loc + 1):
                        print("\b", end="")
                    sys.stdout.flush()
                    a = a[:loc-1] + a[loc:]
                    loc -= 1
            # Backspacing until next space
            if key == "ctrl backspace":
                if len(a) > 0:
                    while not a[loc-1] == " ":
                        for i in range(len(a) - loc + 1):
                            print("\b \b", end="")
                        sys.stdout.write("\b" + a[loc:] + " ")
                        sys.stdout.flush()
                        a = a[:loc-1] + a[loc:]
                        loc -= 1
                        if len(a) <= 0:
                            break
                    if len(a) > 0:
                        print("\b", end="")
                        sys.stdout.flush()
                        a = a[:loc-1] + a[loc:]
                        loc -= 1
            # Returning Back command
            if key == "esc" and (len(a) == 0 or mode == "all") and back:
                sound.play_sound("select")
                return "/B"
            # Breaking input loop and keeping value
            if key == "enter" and textField:
                print("")
                break
            # Opening console
            if key in ("`", "~") and not mode == "command":
                a = ""
                return "/D"
            # Closing console
            if key in ("`", "~") and mode == "command":
                text.set_cursor_visible(False)
                a = ""
                return "/C"
            # Getting last command
            if key == "up" and mode == "command":
                if a:
                    for i in range(len(a) - loc):
                        print(" ")
                        loc += 1
                    for i in range(loc):
                        print("\b \b")
                    sys.stdout.flush()
                
                a = self.lastCommand
                loc = len(a)
                print(a, end="")
                sys.stdout.flush()
        
        text.set_cursor_visible(False)
        
        if a == "":
            return ""
        if not mode == "command":
            return a.lower().strip()
        else:
            self.lastCommand = a
            return a


control = Control()
