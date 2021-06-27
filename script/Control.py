import script.Globals as Globals
from script.Text import text
import os, re, sys, time

if Globals.system == "Windows": import win32gui, msvcrt
else: import tty, termios, select


class Control:
    def __init__(self):
        # Setup input for Linux
        if Globals.system != "Windows":
            orig_settings = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin)

    
    def get_key(self):
        # Get key as soon as one is available
        key = ""
        if Globals.system == "Windows":
            if msvcrt.kbhit():
                key = msvcrt.getch()
                try:
                    key = key.decode("utf-8")
                except:
                    if key == b'\xe0': key = "\xe0"
                    else: key = ""
        else:
            if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
                key = sys.stdin.read(1)[0]
        
        # Returning key names instead of their given values for some cases
        if key == "\n" or key == "\r": return "enter"
        elif key == "\x1b": return "esc"
        elif key == " ": return "space"
        elif key == "\x08": return "backspace"
        elif key == "\x7f": return "ctrl backspace"
        elif key == "\xe0":
            try:
                key = msvcrt.getch().decode("utf-8")
            except:
                key = ""
            if key == "K": return "left"
            elif key == "M": return "right"
            elif key == "H": return "up"
            else: return "down"
        else: return key
    
    
    def wait_for_key(self, key):
        # Blocks code until specified key is pressed
        while 1:
            time.sleep(0.05)
            if self.get_key() == key: break
    
    
    def press_enter(self):
        text.set_cursor_visible(False)
        print(f'\n {text.c("option")}[Press Enter]{text.reset}')
        self.wait_for_key("enter")
        text.set_cursor_visible(True)
    
    
    def get_input(self, mode, textField=True, back=True, options="", prompt=""):
        if textField:
            if mode == "command": print(f'\n{c("option")} Console >| {reset}', end = "")
            else: print(f'\n{c("option")} > {reset}', end = "")
            text.set_cursor_visible(True)
        else:
            if mode == "none": helpText = ""
            elif mode == "alphabetic": helpText = "- Press a letter"
            elif mode == "numeric": helpText = "- Press a number"
            elif mode == "alphanumeric": helpText = "- Press a letter or number"
            
            if back: helpText += ", or press ESC to go back."
            else: helpText += "."
        
        print("\n " + helpText)
        
        a = prompt
        loc = len(prompt)
        print(a, end = "")
        sys.stdout.flush()
        terminalSize = os.get_terminal_size()
        while 1:
            time.sleep(0.05)
            key = self.get_key()
            if terminalSize != os.get_terminal_size(): return "D"
            # Looking for single character keys
            if len(key) == 1 and ((mode in ("command", "all")) or (re.match("[0-9]", key) and mode in ("numeric", "optionumeric", "alphanumeric")) or (re.match("[A-Za-z\_\s\/]", key) and mode in ("alphabetic", "optionumeric", "alphanumeric"))):
                if textField:
                    a = a[:loc] + key + a[loc:]
                    loc += 1
                    print(key + a[loc:], end = "")
                    for i in range(len(a) - loc):
                        print("\b", end = "")
                    sys.stdout.flush()
                elif key in options or key.lower() in options:
                    a = key
                    break
            # Adding a space
            if key == "space" and textField:
                a = a[:loc] + " " + a[loc:]
                loc += 1
                print(" " + a[loc:], end = "")
                for i in range(len(a) - loc):
                    print("\b", end = "")
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
                        print("\b", end = "")
                    sys.stdout.flush()
                    a = a[:loc-1] + a[loc:]
                    loc -= 1
            # Backspacing until next space
            if key == "ctrl backspace":
                if len(a) > 0:
                    while not a[loc-1] == " ":
                        for i in range(len(a) - loc + 1):
                            print("\b \b", end = "")
                        sys.stdout.write("\b" + a[loc:] + " ")
                        sys.stdout.flush()
                        a = a[:loc-1] + a[loc:]
                        loc -= 1
                        if len(a) <= 0: break
                    if len(a) > 0:
                        print("\b", end = "")
                        sys.stdout.flush()
                        a = a[:loc-1] + a[loc:]
                        loc -= 1
            # Returning Back command
            if key == "esc" and (len(a) == 0 or mode == "all") and back:
                return "B"
            # Breaking input loop and keeping value
            if key == "enter" and textField:
                print("")
                break
            """
            # Opening console
            if key in ("`", "~") and mode != "command":
                a = ""
                print("\b \b", end = "")
                sys.stdout.flush()
                command(True, "command")
                return "D"
            # Closing console
            if key in ("`", "~") and mode == "command":
                a = ""
                print("\b \b")
                return "D"
            """
        
        text.set_cursor_visible(False)
        
        if a == "": return ""
        if not mode == "command": return (str.lower(a).strip() if lower else a.strip())
        
        """
        # Running command from console input
        devCommand(a)
        return "D"
        """


control = Control()
