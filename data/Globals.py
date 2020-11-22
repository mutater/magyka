from .Item import *
from .Entity import *
from .Effect import *
from platform import platform
import sys

stackableItems = [
    "consumable",
    "item"
]
unstackableItems = [
    "equipment"
]
slotList = [
    "weapon",
    "tome",
    "head",
    "chest",
    "legs",
    "feet",
    "accessory"
]

def c(color, back = False):
    if platform().split("-")[1] == "10": return ("\x1b[38;5;" if not back else "\x1b[48;5;") + colors[color] + "m"
    else: return ""

def cc(color, back = False):
    if platform().split("-")[1] == "10": return ("\x1b[38;5;" if not back else "\x1b[48;5;") + color + "m"
    else: return ""

def setCursorVisible(visible):
    if platform().split("-")[1] == "10":
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
    "option": "231",
}
reset = "\x1b[0m" if platform().split("-")[1] == "10" else ""

devMode = False
textSpeed = 0.03
returnToScreenName = ""
returnToScreenBool = False
music = ""
screen = ""

# Common    Restore: ingredient, item
# Uncommon  Restore: meal / drink, ingredient, item
# Rare      Restore: meal / drink, ingredient, item
# Epic      Restore: meal / drink, ingredient, vial, item
# Legendary Restore: meal / drink, ingredient, potion, item
# Mythical  Restore: meal / drink, potion, item

# For each tier of potion, cost is (tier - 0.2) * original cost
# For each tier of potion, effect is (tier - 0.25) * original effect
