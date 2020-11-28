import platform
import sys

system = platform.system()
release = platform.release()

ansi = (system == "Windows" and release in ("8", "8.1", "10")) or system == "Linux"

clearCommand = "cls" if system == "Windows" else "clear"

stackableItems = ["consumable", "item"]
unstackableItems = ["equipment"]
slotList = [
    "weapon",
    "tome",
    "head",
    "chest",
    "legs",
    "feet",
    "accessory"]

def c(color, back = False):
    ansiCode = "\x1b[48;5;" if back else "\x1b[38;5;"
    return f'{ansiCode}{colors[color]}m' if ansi else ""

def cc(color, back = False):
    ansiCode = "\x1b[48;5;" if back else "\x1b[38;5;"
    return f'{ansiCode}{color}m' if ansi else ""

def setCursorVisible(visible):
    if ansi:
        print("\x1b[?25h" if visible else "\x1b[?25l", end = "")
        sys.stdout.flush()

colors = {
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
    "green": "010",
    "light blue": "039",
    "blue": "004",
    "dark blue": "018",
    "light purple": "135",
    "purple": "128",
    "option": "231"}
reset = "\x1b[0m" if ansi else ""

textSpeed = 0.03
returnToScreenName = ""
returnToScreenBool = False
screen = ""
