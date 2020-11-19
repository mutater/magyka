"""
ADD DRINKS TO TAVERN
"""

# ::::::.    :::.::::::::::::::::::  :::.      :::     ::::::::::::.,::::::  
# ;;;`;;;;,  `;;;;;;;;;;;;;;'''';;;  ;;`;;     ;;;     ;;;'`````;;;;;;;''''  
# [[[  [[[[[. '[[[[[     [[     [[[ ,[[ '[[,   [[[     [[[    .n[[' [[cccc   
# $$$  $$$ "Y$c$$$$$     $$     $$$c$$$cc$$$c  $$'     $$$  ,$$P"   $$""""   
# 888  888    Y88888     88,    888 888   888,o88oo,.__888,888bo,_  888oo,__ 
# MMM  MMM     YMMMM     MMM    MMM YMM   ""` """"YUMMMMMM `""*UMM  """"YUMMM





import copy
import inspect
import json
import keyboard
import math
import msvcrt
import os
import pickle
import re
import string
import subprocess
import sys
import time
import traceback
import win32gui
print("\n Loading...")
from data.Entity import *
from data.Item import *
from data.Effect import *
from data.Globals import *

windowID = win32gui.GetForegroundWindow()

# .::::::' ...    ::::::.    :::.  .,-:::::  :::::::::::::::    ...     :::.    :::. .::::::. 
# ;;;''''  ;;     ;;;`;;;;,  `;;;,;;;'````'  ;;;;;;;;'''';;; .;;;;;;;.  `;;;;,  `;;;;;;`    ` 
# [[[,,== [['     [[[  [[[[[. '[[[[[              [[     [[[,[[     \[[,  [[[[[. '[['[==/[[[[,
# `$$$"`` $$      $$$  $$$ "Y$c$$$$$              $$     $$$$$$,     $$$  $$$ "Y$c$$  '''    $
#  888    88    .d888  888    Y88`88bo,__,o,      88,    888"888,_ _,88P  888    Y88 88b    dP
#  "MM,    "YmmMMMM""  MMM     YM  "YUMMMMMP"     MMM    MMM  "YMMMMMP"   MMM     YM  "YMmMY" 





# :      :::::  :::::  :::::  :::::
# :      :   :  :        :    :
# :      :   :  : :::    :    :
# :      :   :  :   :    :    :
# :::::  :::::  :::::  :::::  :::::

def ifNone(value, backup):
    if not value == None: return value
    else: return backup

# :::::  :      :::::   :::   :::::  :::::  ::  :  :::::
# :      :      :      :   :  :   :    :    : : :  :
# :      :      :::    :::::  ::::     :    : : :  : :::
# :      :      :      :   :  :   :    :    :  ::  :   :
# :::::  :::::  :::::  :   :  :   :  :::::  :   :  :::::

def clear():
    os.system("cls")
    global screen
    screen = inspect.stack()[1][3]
    setCursorVisible(False)
    os.system(f'mode con: cols={str(os.get_terminal_size()).split(", lines=")[0].replace("os.terminal_size(columns=", "")} lines={str(os.get_terminal_size()).split(", lines=")[1].replace(")", "")}')
    setCursorVisible(False)


# :::::  :::::  :::::  :: ::   :::   :::::  :::::  :::::  ::  :  :::::
# :      :   :  :   :  : : :  :   :    :      :      :    : : :  :
# :::    :   :  ::::   : : :  :::::    :      :      :    : : :  : :::
# :      :   :  :   :  :   :  :   :    :      :      :    :  ::  :   :
# :      :::::  :   :  :   :  :   :    :      :    :::::  :   :  :::::

def openText(path):
    return open(path, "r").read()

def evalText(text):
    return eval(f'f"""{text}"""')

def openTextAsList(path, splitter = "|"):
    return open(path, "r").read().split(splitter)

def evalTextAsList(path, splitter = "|"):
    return [eval(i) for i in open(path, "r").read().split(splitter)]

def printEvalText(string):
    print(evalText(string))


# :::::  :::::  :: ::  :: ::   :::   ::  :  ::::   :::::
# :      :   :  : : :  : : :  :   :  : : :  :   :  :
# :      :   :  : : :  : : :  :::::  : : :  :   :  :::::
# :      :   :  :   :  :   :  :   :  :  ::  :   :      :
# :::::  :::::  :   :  :   :  :   :  :   :  ::::   :::::


def command(input = False, mode = "alphabetic", back = True, silent = False, lower = True, options = "", prompt = "", callback = ""):
    if input:
        if mode == "command": print(f'\n{c("option")} Console >| {reset}', end = "")
        else: print(f'\n{c("option")} > {reset}', end = "")
        setCursorVisible(True)
    elif silent: pass
    elif mode == "none": print("\n Press ESC to go back.")
    elif mode == "alphabetic": print("\n  -  Press a letter" + (", or ESC to go back." if back else "."))
    elif mode == "numeric": print("\n  -  Press a number, or ESC to go back.")
    elif mode == "optionumeric": print("\n  -  Press a number or letter, or ESC to go back.")

    a = prompt
    loc = len(prompt)
    print(a, end = "")
    sys.stdout.flush()
    while 1:
        key = keyboard.read_event()
        if key.event_type == "down" and win32gui.GetForegroundWindow() == windowID:
            if callback != "" and keyboard.is_pressed(callback): return "D"
            if not any([keyboard.is_pressed(key) for key in ["ctrl", "alt", "win"]]):
                if len(key.name) == 1 and (mode == "command" or mode == "all" or (re.match("[0-9]", key.name) and mode in ("numeric", "optionumeric", "alphanumeric")) or (re.match("[A-Za-z\_\s\/]", key.name) and mode in ("alphabetic", "optionumeric", "alphanumeric"))):
                    if input:
                        a = a[:loc] + key.name + a[loc:]
                        loc += 1
                        print(key.name + a[loc:], end = "")
                        for i in range(len(a) - loc):
                            print("\b", end = "")
                        sys.stdout.flush()
                    elif (re.match("[^A-Z]", key.name) or keyboard.is_pressed("shift")) and key.name in options:
                        a = a[loc:] + key.name + a[:loc]
                        break
                if key.name == "space" and input:
                    a = a[:loc] + " " + a[loc:]
                    loc += 1
                    print(" " + a[loc:], end = "")
                    for i in range(len(a) - loc):
                        print("\b", end = "")
                    sys.stdout.flush()
                if key.name == "left" and loc > 0:
                    loc -= 1
                    sys.stdout.write("\b")
                    sys.stdout.flush()
                if key.name == "right" and loc < len(a):
                    loc += 1
                    sys.stdout.write(a[loc-1])
                    sys.stdout.flush()
                if key.name == "backspace":
                    if len(a) > 0:
                        sys.stdout.write("\b" + a[loc:] + " ")
                        for i in range(len(a) - loc + 1):
                            print("\b", end = "")
                        sys.stdout.flush()
                        a = a[:loc-1] + a[loc:]
                        loc -= 1
                if key.name == "f11":
                    return "D"
                if key.name == "esc" and (len(a) == 0 or mode == "all") and back:
                    return "B"
                if key.name == "enter" and input:
                    print("")
                    break
                if key.name == "`" and mode != "command":
                    a = ""
                    print("\b \b", end = "")
                    sys.stdout.flush()
                    command(True, "command")
                    return "D"
                if key.name == "`" and mode == "command":
                    a = ""
                    print("\b \b")
                    return "D"
            if key.name == "backspace" and keyboard.is_pressed("ctrl") and not keyboard.is_pressed("alt"):
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
            if key.name == "backspace" and keyboard.is_pressed("ctrl") and keyboard.is_pressed("alt"):
                for i in range(len(a)):
                    sys.stdout.write("\b \b")
                sys.stdout.flush()
                a = ""
            if key.name == "enter" and keyboard.is_pressed("alt"):
                return "D"
            if key.name == "up" and keyboard.is_pressed("win"):
                return "D"

    setCursorVisible(False)

    if a == "": return ""
    if not mode == "command": return (str.lower(a).strip() if lower else a.strip())

    a1 = a.split(" ", 1)
    a2 = a.split(" ", 2)

    if a1[0] == "equip":
        if a1[1] in items:
            try:
                if player.equipment[items[a1[1]]["slot"]] != "": player.unequip(items[a1[1]]["slot"])
                player.equip(newItem(a1[1]))
            except:
                print(c("light red") + "\n That didn't work, stupid." + reset)
                pressEnter()
    elif a1[0] == "exec":
        try: exec(a1[1])
        except:
            print(c("light red") + "\n " + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            pressEnter()
    elif a1[0] == "execp":
        try: print("\n " + str(eval(a1[1])))
        except:
            print(c("light red") + "\n " + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]) + reset)
        pressEnter()
    elif a == "flee":
        returnToScreen("s_explore")
    elif a1[0] == "fight":
        if a1[1] in enemies:
            try: 
                s_battle(newEnemy(a1[1]))
            except:
                print(c("light red") + "\n That didn't work, stupid." + reset)
                pressEnter()
    elif a1[0] == "get":
        a1s = a1[1].split(", ")
        try: player.getDrops(int(a1s[0]), int(a1s[1]))
        except:
            print(c("light red") + "\n That didn't work, stupid." + reset)
            pressEnter()
    elif a1[0] == "give":
        a1s = a1[1].split(", ")
        if a1s[0] == "all":
            for item in items:
                player.addItem(newItem(item))
        if a1s[0] in items:
            try:
                for i in range((int(a1s[1]) if len(a1s) == 2 else 1)):
                    player.addItem(newItem(a1s[0]))
            except:
                print(c("light red") + "\n That didn't work, stupid." + reset)
                pressEnter()
    elif a == "levelup":
        player.getDrops(player.mxp - player.xp, 0)
    elif a1[0] == "name":
        player.name = a1[1].strip()
    elif a == "quit":
        sys.exit()
    elif a == "clear passives":
        player.passives = []
        player.updateStats()
    elif a == "restore":
        player.hp, player.mp = player.stats["max hp"], player.stats["max mp"]
    elif a == "restart":
        if settings["fullscreen"]: fullscreen()
        os.execv(sys.executable, ['python'] + sys.argv)
    elif a == "s":
        player.name = "Developer"
        s_camp()
    else:
        print(c("light red") + "\n That's not a command, stupid." + reset)
        pressEnter()

    return "D"


# :::::  ::  :  :::::  :   :  :::::
#   :    : : :  :   :  :   :    :
#   :    : : :  :::::  :   :    :
#   :    :  ::  :      :   :    :
# :::::  :   :  :      :::::    :


def options(names):
    if len(names) > 0: print("")
    for i in range(len(names)):
        print(f' {c("option") + c("dark gray", True)}[{names[i][11 if ";" in names[i] else 0]}]{reset} {names[i]}')
        if i < len(names)-1: print(f' {c("option") + c("dark gray", True)} | {reset}')
    print(reset, end="")

def pressEnter(prompt = f'\n {c("option")}[Press Enter]{reset}'):
    print(prompt)
    keyboard.wait("enter")
    while 1:
        if not win32gui.GetForegroundWindow() == windowID: keyboard.wait("enter")
        else: break

def fullscreen():
    keyboard.remove_hotkey("alt + enter")
    keyboard.press_and_release("alt + enter")
    keyboard.add_hotkey("alt + enter", blockAltEnter)


# :::::  :::::  :::::  :   :  :::::  ::  :
# :   :  :        :    :   :  :   :  : : :
# ::::   :::      :    :   :  ::::   : : :
# :   :  :        :    :   :  :   :  :  ::
# :   :  :::::    :    :::::  :   :  :   :


def returnTo():
    global returnToScreenBool, screen
    screen = inspect.stack()[1][3]
    if returnToScreenBool and screen != returnToScreenName: return True
    if screen == returnToScreenName:
        returnToScreenBool = False
        return False

def returnToScreen(screen):
    global returnToScreenBool, returnToScreenName
    returnToScreenBool = True
    returnToScreenName = screen


# :::::  :::::  :::::  ::  :  :::::  :::::  ::  :  :::::
# :   :  :   :    :    : : :    :      :    : : :  :
# :::::  ::::     :    : : :    :      :    : : :  : :::
# :      :   :    :    :  ::    :      :    :  ::  :   :
# :      :   :  :::::  :   :    :    :::::  :   :  :::::


def write(text, speed = textSpeed):
    i = 0
    delay = speed
    canSkip = not keyboard.is_pressed("enter")
    while i < len(text):
        if text[i:i+2] == "0m":
            print(reset, end="")
            i += 1
        elif text[i:i+5] == "38;5;":
            print("\x1b[" + text[i:i+10], end="")
            i += 9
        elif text[i] == "#":
            pressEnter()
            delay = speed
        elif text[i] == "<":
            clear()
            delay = speed
        else:
            print(text[i], end="")
        time.sleep(delay)
        if not canSkip and not keyboard.is_pressed("enter"): canSkip = True
        if canSkip and keyboard.is_pressed("enter"): delay = 0
        sys.stdout.flush()
        while msvcrt.kbhit(): msvcrt.getwch()
        i += 1
    print("\n")

def drawBar(max, value, color, length):
    text = "".center(length, "■")
    if round(value/max*length) > 0: text = c(color) + c("dark " + color, True) + text[:round((value/max)*length)] + c("gray") + c("dark gray", True) + text[round((value/max)*length):] + reset
    else: text = c("gray") + c("dark gray", True) + text + reset
    return text

def displayItem(name, rarity, quantity = 0):
    amt = ("" if quantity == 0 else " x" + str(quantity))
    if rarity == "common": return c("lightish gray") + name + reset + amt
    if rarity == "uncommon": return c("lightish green") + name + reset + amt
    if rarity == "rare": return c("light blue") + name + reset + amt
    if rarity == "epic": return c("light purple") + name + reset + amt
    if rarity == "legendary": return c("light orange") + name + reset + amt
    if rarity == "mythical": return c("lightish red") + name + reset + amt

def displayEffect(effects):
    if "-hp" in effects or "-mp" in effects or "-all" in effects:
        if "-hp" in effects:
            if type(effects["-hp"]["value"]) is list:
                damage = f'{c("red")}{effects["-hp"]["value"][0]} - {effects["-hp"]["value"][1]}{"%" if "*" in effects["-hp"] else ""} ♥{reset}'
            else:
                damage = f'{c("red")}{effects["-hp"]["value"]}{"%" if "*" in effects["-hp"] else ""} ♥{reset}'
            effect = "-hp"
        if "-mp" in effects:
            if type(effects["-mp"]["value"]) is list:
                damage = f'{c("blue")}{effects["-mp"]["value"][0]} - {effects["-mp"]["value"][1]}{"%" if "*" in effects["-mp"] else ""} ♦{reset}'
            else:
                damage = f'{c("blue")}{effects["-mp"]["value"]}{"%" if "*" in effects["-mp"] else ""} ♦{reset}'
            effect = "-mp"
        if "-all" in effects:
            if type(effects["-all"]["value"][0]) is list:
                damage = f'{c("red")}{effects["-all"]["value"][0][0]} - {effects["-all"]["value"][0][1]}{"%" if "*" in effects["-all"] else ""} ♥{reset} and '
            else:
                damage = f'{c("red")}{effects["-all"]["value"][0]}{"%" if "*" in effects["-all"] else ""} ♥{reset} and '
            if type(effects["-all"]["value"][1]) is list:
                damage += f'{c("blue")}{effects["-all"]["value"][1][0]} - {effects["-all"]["value"][1][1]}{"%" if "*" in effects["-all"] else ""} ♦{reset}'
            else:
                damage += f'{c("blue")}{effects["-all"]["value"][1]}{"%" if "*" in effects["-all"] else ""} ♦{reset}'
            effect = "-all"
        print(f'\n Deals {damage} damage')
        if "crit" in effects[effect]: print(f' - {effects[effect]["crit"]}% critical strike chance')
        if "hit" in effects[effect]: print(f' - {effects[effect]["hit"]}% hit chance')
        if "dodge" in effects[effect]: print(f' - Undodgeable')
    if "hp" in effects or "mp" in effects or "all" in effects:
        if "hp" in effects:
            if type(effects["hp"]["value"]) is list:
                heal = f'{c("red")}{effects["hp"]["value"][0]} - {effects["hp"]["value"][1]}{"%" if "*" in effects["hp"] else ""} ♥{reset}'
            else:
                heal = f'{c("red")}{effects["hp"]["value"]}{"%" if "*" in effects["hp"] else ""} ♥{reset}'
            effect = "hp"
        if "mp" in effects:
            if type(effects["mp"]["value"]) is list:
                heal = f'{c("blue")}{effects["mp"]["value"][0]} - {effects["mp"]["value"][1]}{"%" if "*" in effects["mp"] else ""} ♦{reset}'
            else:
                heal = f'{c("blue")}{effects["mp"]["value"]}{"%" if "*" in effects["mp"] else ""} ♦{reset}'
            effect = "mp"
        if "all" in effects:
            if type(effects["all"]["value"][0]) is list:
                heal = f'{c("red")}{effects["all"]["value"][0][0]} - {effects["all"]["value"][0][1]}{"%" if "*" in effects["all"] else ""} ♥{reset} and '
            else:
                heal = f'{c("red")}{effects["all"]["value"][0]}{"%" if "*" in effects["all"] else ""} ♥{reset} and '
            if type(effects["all"]["value"][1]) is list:
                heal += f'{c("blue")}{effects["all"]["value"][1][0]} - {effects["all"]["value"][1][1]}{"%" if "*" in effects["all"] else ""} ♦{reset}'
            else:
                heal += f'{c("blue")}{effects["all"]["value"][1]}{"%" if "*" in effects["all"] else ""} ♦{reset}'
            effect = "all"
        print(f'\n Heals {heal}')
        if effect in ("hp", "all"): displayPlayerHP()
        if effect in ("mp", "all"): displayPlayerMP()
    if any([stat in effects for stat in player.stats]): print("")
    if "attack" in effects: print(f' {effects["attack"]["value"][0]} - {effects["attack"]["value"][1]} Damage')
    for stat in ("armor", "strength", "intelligence", "vitality", "agility", "max hp", "max mp"):
        if stat in effects:
            if stat == "max hp":
                color, character = c("red"), " ♥"
            elif stat == "max mp":
                color, character = c("blue"), " ♦"
            else:
                color, character = "", ""
            
            if "*" in effects[stat]:
                print(f' {abs(effects[stat]["value"])}% {"Increased" if effects[stat]["value"] > 0 else "Decreased"} {color}{stat.capitalize()}{character}{reset}')
            else:
                print(f' {"+" if effects[stat]["value"] > 0 else ""}{effects[stat]["value"]} {color}{stat.capitalize()}{character}{reset}')
    for stat in ("crit", "hit", "dodge"):
        if stat in effects: print(f' {abs(effects[stat]["value"])}% {"Increased" if effects[stat]["value"] > 0 else "Decreased"} {stat.capitalize()} Chance')

def displayItemStats(item):
    print("\n " + displayItem(item["name"], item["rarity"]))
    print("  " + item["description"])
    print(" " + item["rarity"].capitalize())

    effects = {}
    p_passives = []
    if item["type"] != "item":
        for effect in item["effect"]:
            if effect["type"] == "passive":
                p_passives.append(passives[effect["name"]])
            else:
                effects.update({effect["type"]: effect})
    if item["type"] == "equipment" and item["slot"] == "tome": print(f'\n Costs {c("blue")}{item["mana"]} ♦{reset}')
    displayEffect(effects)
    for effect in p_passives:
        if effect["buff"]:
            effectColor = "light green"
        else:
            effectColor = "light red"
        
        if type(effect["turns"]) is list:
            turnText = f'{effect["turns"][0]} - {effect["turns"][1]} turns'
        else:
            turnText = f'{effect["turns"]} turn{"s" if effect["turns"] > 1 else ""}'
        
        print(f'\n Applies {c(effectColor)}{effect["name"]}{reset} for {turnText}')
        if "crit" in effect: print(f' - {effect["crit"]}% critical strike chance')
        if "hit" in effect: print(f' - {effect["hit"]}% hit chance')
        if "dodge" in effect: print(f' - Undodgeable')

def displayPlayerTitle():
    print(f' {player.name} [Lvl {player.level}]')

def displayPlayerHP():
    print(f' {c("red")}♥ {drawBar(player.stats["max hp"], player.hp, "red", 20)} {player.hp}/{player.stats["max hp"]}')

def displayPlayerMP():
    print(f' {c("blue")}♦ {drawBar(player.stats["max mp"], player.mp, "blue", 20)} {player.mp}/{player.stats["max mp"]}')

def displayPlayerXP():
    print(f' XP: {c("green")}◌{reset} {player.xp}/{player.mxp}')

def displayPlayerGold():
    print(f' Gold: {c("yellow")}● {reset}{player.gold}')

def displayPlayerPassives():
    if len(player.passives) > 0:
        print(" ", end="")
        print(", ".join([f'{c("light green" if passive["buff"] else "light red")}{passive["name"]}{reset} ({passive["turns"]})' for passive in player.passives]))

def displayPlayerStats():
    print("")
    displayPlayerTitle()
    displayPlayerHP()
    displayPlayerMP()
    displayPlayerXP()
    displayPlayerGold()
    displayPlayerPassives()

def displayBattleStats(player, enemy, playerDamage = 0, enemyDamage = 0):
        if playerDamage > 0: playerDamageText = " +" + str(playerDamage)
        elif playerDamage < 0: playerDamageText = " " + str(playerDamage)
        else: playerDamageText = ""
        if enemyDamage > 0: enemyDamageText = " +" + str(enemyDamage)
        elif enemyDamage < 0: enemyDamageText = " " + str(enemyDamage)
        else: enemyDamageText = ""
        print(f'\n -= {player.name} Versus {enemy.name} [Lvl {enemy.level}] =-')
        print(f'\n {player.name}')
        print(f' {c("red")}♥ {drawBar(player.stats["max hp"], player.hp, "red", 20)} {player.hp}/{player.stats["max hp"]}{playerDamageText}')
        print(f' {c("blue")}♦ {drawBar(player.stats["max mp"], player.mp, "blue", 20)} {player.mp}/{player.stats["max mp"]}')
        displayPlayerPassives()
        print(f'\n {enemy.name} [Lvl {enemy.level}]')
        print(f' {c("red")}♥ {drawBar(enemy.stats["max hp"], enemy.hp, "red", 20)} {enemy.hp}/{enemy.stats["max hp"]}{enemyDamageText}')
        print(f' {c("blue")}♦ {drawBar(enemy.stats["max mp"], enemy.mp, "blue", 20)} {enemy.mp}/{enemy.stats["max mp"]}')
        if len(enemy.passives) > 0:
            print(" ", end="")
            print(", ".join([f'{c("light green" if passive["buff"] else "light red")}{passive["name"]}{reset} ({passive["turns"]})' for passive in enemy.passives]))



#  .::::::.   .,-:::::  :::::::..   .,::::::  .,::::::  :::.    :::. .::::::. 
# ;;;`    ` ,;;;'````'  ;;;;``;;;;  ;;;;''''  ;;;;''''  `;;;;,  `;;;;;;`    ` 
# '[==/[[[[,[[[          [[[,/[[['   [[cccc    [[cccc     [[[[[. '[['[==/[[[[,
#   '''    $$$$          $$$$$$c     $$""""    $$""""     $$$ "Y$c$$  '''    $
#  88b    dP`88bo,__,o,  888b "88bo, 888oo,__  888oo,__   888    Y88 88b    dP
#   "YMmMY"   "YUMMMMMP" MMMM   "W"  """"YUMMM """"YUMMM  MMM     YM  "YMmMY" 





# :: ::   :::   :::::  ::  :      :: ::  :::::  ::  :  :   :
# : : :  :   :    :    : : :      : : :  :      : : :  :   :
# : : :  :::::    :    : : :      : : :  :::    : : :  :   :
# :   :  :   :    :    :  ::      :   :  :      :  ::  :   :
# :   :  :   :  :::::  :   :      :   :  :::::  :   :  :::::


def s_mainMenu():
    i = 0
    while 1:
        i += 1
        clear()
        if i == 1: write("\n Welcome to the world of...")
        else: print("\n Welcome to the world of...\n")

        title = openTextAsList("data//text//magyka title.txt", splitter = "\n")
        for i in range(len(title)):
            print(cc(["026", "012", "006", "039", "045", "019", "020", "021", "004", "027", "026", "012", "006", "039", "000", "039", "006", "012"][i]) + title[i] + reset)

        options(["New Game", "Continue", "Options", "Quit"])
        option = command(back = False, options = "ncoq")

        if option == "n": s_newGame()
        elif option == "c": s_continue()
        elif option == "o": s_options()
        elif option == "q": sys.exit()
        if returnTo(): break

def s_newGame():
    clear()

    text = openTextAsList("data//text/new game.txt")
    write(evalText(text[0]), textSpeed)

    while 1:
        option = command(True, "alphanumeric", back = False)

        if option == "" or option == None: print(c("light red") + "\n Your name cannot be empty." + reset)
        elif len(option) >= 15: print(c("light red") + "\n Your name cannot be over 15 characters." + reset)
        elif not re.match("[\w\s\ ]", option): print(c("light red") + "\n Your name contains illegal characters." + reset)
        else:
            player.name = (string.capwords(option))
            break

        pressEnter()
        clear()
        write(evalText(text[0]), 0)

    write(evalText(text[1]), textSpeed)
    s_camp()

def s_continue():
    global saves, player
    while 1:
        clear()

        print("\n -= Load =-")
        print("\n Which file are you loading?")

        if len(saves) > 0: print("")
        else: print("\n " + c("dark gray") + "- Empty -" + reset)

        for i in range(len(saves)):
            print(f' {i}) {saves[i][1]} | {saves[i][0].name} [Lvl {saves[i][0].level}]')

        option = command(False, "optionumeric", options = "".join(tuple(map(str, range(0, len(saves))))))

        if option in tuple(map(str, range(0, len(saves)))):
            player = saves[int(option)][0]
            s_camp()
        elif option in ("B"): break
        if returnTo(): break

def s_options():
    while 1:
        clear()

        print("\n -= Options =-\n")
        print(f' {c("option")}1){reset} Fullscreen: ({c("light green") + "ON" if settings["fullscreen"] else c("light red") + "OFF"}{reset})')

        option = command(False, "numeric", options = "1")

        if option == "1":
            fullscreen()
            settings["fullscreen"] = False if settings["fullscreen"] else True
        elif option == "B":
            with open("data\\settings.json", "w+") as settingsFile:
                json.dump(settings, settingsFile)
            break


# :::::   :::   :: ::  :::::
# :      :   :  : : :  :   :
# :      :::::  : : :  :::::
# :      :   :  :   :  :
# :::::  :   :  :   :  :


def s_camp():
    while 1:
        if returnTo(): break
        clear()

        print("\n -= Camp =-")
        displayPlayerStats()
        printEvalText(openText("data//text//screens//camp.txt"))
        
        options(["Explore", "Town", "Character", "Options", "Save", "Quit"])
        option = command(back = False, options = "etcosq")

        if option == "e": s_explore()
        elif option == "t": s_town()
        elif option == "c": s_character()
        elif option == "o": s_options()
        elif option == "s": s_save()
        elif option == "q": s_quit()


# :::::  :   :  :::::  :      :::::  :::::  :::::
# :       : :   :   :  :      :   :  :   :  :
# :::      :    :::::  :      :   :  ::::   :::
# :       : :   :      :      :   :  :   :  :
# :::::  :   :  :      :::::  :::::  :   :  :::::


def s_explore():
    while 1:
        clear()

        print("\n -= Explore =-")
        displayPlayerStats()
        printEvalText(openText(f'data//text//screens//{player.location} explore.txt'))

        options(["Hunt", c("dark gray") + "Search", c("dark gray") + "Location", c("dark gray") + "Map"])
        option = command(options = "hslm")

        if option == "h":
            areaEnemies = loadEncounter(player.location, "hunt")
            
            weight = 0
            level = randint(1, 4)
            if level == 1: level = player.level if player.level > 1 else 1
            elif level <= 3: level = player.level
            else: level = player.level + 1

            for i in range(len(areaEnemies)):
                areaEnemies[i][1].levelDifference = level - areaEnemies[i][1].level[0] if level - areaEnemies[i][1].level[0] >= 0 else 0
                areaEnemies[i][1].level = max(min(level, areaEnemies[i][1].level[1]), areaEnemies[i][1].level[0])
                areaEnemies[i][0] += (areaEnemies[i][1].level - player.level) * -50 if areaEnemies[i][1].level - player.level > 0 else 0
                if areaEnemies[i][0] < 1: areaEnemies[i][0] = 1
                
                for stat in areaEnemies[i][1].baseStats:
                    for j in range(1, abs(areaEnemies[i][1].levelDifference) + 1):
                        if stat in ("strength", "intelligence", "vitality"):
                            areaEnemies[i][1].baseStats[stat] += 0.5
                        elif stat in ("max hp", "max mp"):
                            areaEnemies[i][1].baseStats[stat] = math.ceil(areaEnemies[i][1].baseStats[stat] * 1.1)
                    if stat in ("strength", "intelligence", "vitality"):
                        areaEnemies[i][1].baseStats[stat] = math.floor(areaEnemies[i][1].baseStats[stat])
                areaEnemies[i][1].updateStats()
                areaEnemies[i][0] = int(areaEnemies[i][0]) + weight
                weight += areaEnemies[i][0] - weight

            areaEnemies = dict(areaEnemies)
            enemyNum = randint(1, weight)
            for enemy in areaEnemies:
                if enemyNum <= enemy:
                    enemy = areaEnemies[enemy]
                    break

            print(f'\n You spot {enemy.name} [Lvl {enemy.level}]. Do you fight?')

            options(["Yes", "No"])
            print("\n Press a letter.")
            while 1:
                option1 = command(back = False, silent = True, options = "yn")

                if option1 in ("y", "yes"):
                    s_battle(enemy)
                    break
                elif option1 in ("n", "no"):
                    print(f'\n You quiety slip away from {enemy.name} [Lvl {enemy.level}].')
                    pressEnter()
                    break
        elif option == "s": pass
        elif option == "l": pass
        elif option == "m": pass
        elif option == "B": break
        if returnTo(): break

def s_battle(enemy):
    itemLog = []
    if type(enemy.level) is list: enemy.level = enemy.level[0]

    while 1:
        player.guard = ""
        text = [""]
        playerDamage, enemyDamage = 0, 0
        while 1:
            clear()
            displayBattleStats(player, enemy)
            
            usedItem = False
            canUseMagic = False if player.equipment["tome"] == "" or player.mp < player.equipment["tome"]["mana"] else True

            options(["Attack", (c("dark gray") if not canUseMagic else "") + "Magic", "Guard", "Item", "Flee"])
            option = command(back = False, options = "amgif" if canUseMagic else "agif")

            if enemy.guard == "counter":
                text[0], playerDamage = player.defend(enemy.attack(), enemy.stats)
                text[0] = f'\n {player.name} attacks {enemy.name}, ' + evalText(text[0])
                break
            if option == "a":
                text[0], enemyDamage = enemy.defend(player.attack(), player.stats)
                text[0] = f'\n {player.name} attacks {enemy.name}, ' + evalText(text[0])
                break
            elif option == "m":
                text[0] = f'\n {player.name} casts {player.equipment["tome"]["attackName"]} on {player.name if player.equipment["tome"]["target"] == "self" else enemy.name}, '
                for effect in player.get_magic():
                    if "passive" in effect: passive = passives[effect["passive"]]
                    else: passive = False
                    
                    if player.equipment["tome"]["target"] == "self":
                        tempText, tempDamage = player.defend(effect, player.stats, passive=passive)
                        playerDamage += tempDamage
                        text[0] += evalText(tempText)
                    else:
                        tempText, tempDamage = enemy.defend(effect, player.stats, passive=passive)
                        enemyDamage += tempDamage
                        text[0] += evalText(tempText)
                player.mp -= player.equipment["tome"]["mana"]
                break
            elif option == "g":
                guardState = randint(1, 5)
                if guardState <= 3: player.guard = "deflect"
                elif guardState == 4: player.guard = "block"
                else: player.guard = "counter"
                text[0] = f'\n {player.name} lowers into a defensive stance.'
                break
            elif option == "i":
                page = 1
                while 1:
                    clear()

                    itemList = [item for item in player.inventory if item[0]["type"] == "consumable"]
                    next = len(itemList) > page*10 + 1
                    previous = page != 1

                    displayBattleStats(player, enemy)
                    print("\n Type the number of the item you wish to consume.\n")

                    for i in range(-10 + 10*page, 10*page if 10*page < len(itemList) else len(itemList)):
                        print(f' {str(i)[:-1]}({str(i)[-1]}) {displayItem(itemList[i][0]["name"], itemList[i][0]["rarity"], itemList[i][1])}')

                    if len(itemList) == 0:
                        print(" " + c("dark gray") + "- Empty -" + reset)

                    options((["Next"] if next else []) + (["Previous"] if previous else []))
                    option = command(False, "optionumeric", options = ("n" if next else "") + ("p" if previous else "") + "".join(tuple(map(str, range(0, len(itemList))))))

                    if option in tuple(map(str, range(0, len(itemList)))):
                        item = itemList[int(option) + (page-1) * 10][0]
                        while 1:
                            clear()
                            player.updateStats()

                            print(f'\n -= Inspect Consumable =-')

                            displayItemStats(item)
                            print(f'\n Sell Price: {c("yellow")}● {reset}{item["value"]}')

                            options(["Use"])
                            option1 = command(False, "alphabetic", options = "u")

                            usedItem = False
                            if option1 == "u":
                                text[0] = f'\n {player.name} {item["useVerb"]} {displayItem(item["name"], item["rarity"], 1)}{"" if item["target"] == "self" else " on " + enemy.name}, '
                                for effect in item["effect"]:
                                    if "passive" in effect: passive = passives[effect["passive"]]
                                    else: passive = False
                                    
                                    if item["target"] == "self":
                                        tempText, tempDamage = player.defend(effect, player.stats, passive=passive)
                                        playerDamage += tempDamage
                                        text[0] += evalText(tempText)
                                    else:
                                        tempText, tempDamage = enemy.defend(effect, player.stats, passive=passive)
                                        enemyDamage += tempDamage
                                        text[0] += evalText(tempText)

                                player.removeItem(item)

                                itemFound = False
                                for i in itemLog:
                                    if i[0]["name"] == item["name"]:
                                        i[1] += 1
                                        itemFound = True
                                        break
                                if not itemFound: itemLog.append([item, 1])
                                break
                            elif option1 == "B": break
                        if usedItem: break
                    elif option == "n" and next: page += 1
                    elif option == "p" and previous: page -= 1
                    elif option == "B": break
            elif option == "f":
                while 1:
                    clear()

                    print("\n -= Flee =-")
                    print(f'\n Are you sure you want to flee from {enemy.name} [Lvl {enemy.level}]?')

                    options(["Yes"])
                    option = command(options = "y")

                    if option == "y":
                        if randint(1, 3) == 1:
                            goldLoss = enemy.gold//4 if player.gold - enemy.gold//4 >= 0 else player.gold
                            print(f'\n While fleeing, {player.name} loses {c("yellow")}●{reset} {goldLoss}.')
                            player.gold -= goldLoss
                            pressEnter()
                            returnToScreen("s_explore")
                            return
                        else:
                            print(f'\n {player.name} attempts to flee, but fails.')
                            pressEnter()
                            break
                    elif option == "B": break
                if option == "y": break
            if returnTo(): return
            if usedItem: break

        text += player.update()
        clear()
        displayBattleStats(player, enemy, playerDamage=playerDamage, enemyDamage=enemyDamage)
        playerDamage, enemyDamage = 0, 0
        for line in text:
            print(evalText(line))
        if enemy.hp <= 0 or player.hp <= 0: break
        pressEnter()

        # LOGIC FOR ENEMY ATTACK
        enemy.guard = ""
        text = [""]
        attackType = randint(1,5)
        if attackType <= 2: attackType = "attack"
        elif attackType <= 4: attackType = "magic"
        else: attackType = "guard"

        if player.guard == "counter":
            text[0], enemyDamage = enemy.defend(player.attack(), player.stats)
            text[0] = f'\n {player.name} attacks {enemy.name}, ' + evalText(text[0])
            attackType = ""
        if attackType == "magic":
            if enemy.magic != None:
                castable = []
                for effect in enemy.magic:
                    if enemy.magic["mana"] <= enemy.mp: castable.append(effect)
                if len(castable) == 0: attackType = "attack"
                else:
                    magic = castable[randint(1, len(castable))]

                    for effect in magic["effect"]:
                        if "passive" in effect: passive = passives[effect["passive"]]
                        else: passive = False
                        
                        if magic["target"] == "self":
                            tempText, tempDamage = enemy.defend(effect, enemy.stats, passive=passive)
                            enemyDamage += tempDamage
                            text[0] += evalText(tempText)
                        else:
                            tempText, tempDamage = player.defend(effect, enemy.stats, passive=passive)
                            playerDamage += tempDamage
                            text[0] += evalText(tempText)
                    enemy.mp -= magic["mana"]
            else: attackType = "attack"
        if attackType == "guard":
            if enemy.hp <= enemy.stats["max hp"] // 2:
                guardState = randint(1, 5)
                if guardState <= 3: enemy.guard = "deflect"
                elif guardState == 4: enemy.guard = "block"
                else: enemy.guard = "counter"
                print(f'\n {enemy.name} lowers into a defensive stance.')
            else: attackType = "attack"
        if attackType == "attack":
            text[0], playerDamage = player.defend(enemy.attack(), enemy.stats)
            text[0] = f'\n {enemy.name} attacks {player.name}, ' + evalText(text[0])

        text += player.update()
        clear()
        displayBattleStats(player, enemy, playerDamage=playerDamage, enemyDamage=enemyDamage)
        for line in text:
            print(evalText(line))
        if enemy.hp <= 0 or player.hp <= 0: break
        pressEnter()
    pressEnter()
    
    if enemy.hp <= 0:
        clear()

        print("\n -= Victory =-")

        levelDifference = enemy.level - player.level
        if levelDifference == 0: lootMultiplier = 1
        else: lootMultiplier = max(round(1.25 ** levelDifference, 2), 0.6)
        xp = math.ceil(enemy.xp * lootMultiplier)
        gold = math.ceil(randint(math.ceil(enemy.gold*0.9), math.ceil(enemy.gold*1.1)) * lootMultiplier)
        items = []
        if enemy.items != None:
            for item in enemy.items:
                if randint(1, 100) <= item["chance"]:
                    if type(item["quantity"]) is list: items.append([newItem(item["name"]), randint(item["quantity"][0], item["quantity"][1])])
                    else: items.append([newItem(item["name"]), item["quantity"]])

        if player.getDrops(xp, gold, items): print(f'\n {player.name} Leveled up to level {player.level}!')
        print(f'\n You defeated {enemy.name} [Lvl {enemy.level}] in battle!')
        print("\n Items used: " + (c("gray") + "- None -" + reset if len(itemLog) < 1 else ""))

        for item in itemLog:
            print(f' - {displayItem(item[0]["name"], item[0]["rarity"], item[1])}')

        itemLog = []
        print("\n Obtained: ")
        for item in items:
            print(f' - {displayItem(item[0]["name"], item[0]["rarity"], item[1])}')
        print(f' - XP: {c("green")}◌{reset} {xp} (x{lootMultiplier})')
        print(f' - Gold: {c("yellow")}●{reset} {gold} (x{lootMultiplier})')
        pressEnter()
        return
    else:
        clear()

        print("\n -= Defeat =-")
        print("\n Defeated by:")
        print(f'\n {enemy.name} [Lvl {enemy.level}]')
        print(f' {c("red")}♥ {drawBar(enemy.stats["max hp"], enemy.hp, "red", 20)} {enemy.hp}/{enemy.stats["max hp"]}')
        print(f' {c("blue")}♦ {drawBar(enemy.stats["max mp"], enemy.mp, "blue", 20)} {enemy.mp}/{enemy.stats["max mp"]}')
        
        if len(enemy.passives) > 0:
            print(" ", end="")
            print(", ".join([f'{c("light green" if passive["buff"] else "light red")}{passive["name"]}{reset} ({passive["turns"]})' for passive in enemy.passives]))
        print("\n Items used: " + (c("gray") + "- None -" + reset if len(itemLog) < 1 else ""))

        for item in itemLog:
            print(f' - {displayItem(item[0]["name"], item[0]["rarity"], item[1])}')

        itemLog = []
        player.addPassive(newPassive("Charon's Curse"))
        player.updateStats()
        player.hp = player.stats["max hp"]
        player.mp = player.stats["max mp"]//3
        pressEnter()
        return


# :::::  :::::  :   :  ::  :
#   :    :   :  :   :  : : :
#   :    :   :  : : :  : : :
#   :    :   :  : : :  :  ::
#   :    :::::  :::::  :   :


def s_town():
    while 1:
        clear()

        print("\n -= Town of Fordsville =-")
        displayPlayerStats()
        printEvalText(openText(f'data//text//screens//{player.location} town.txt'))

        options(["Tavern", "General Store", "Blacksmith", "Arcanist", "Flea Market"])
        option = command(options = "tgbaf")

        if option == "t": s_tavern()
        elif option == "g": s_store("general store")
        elif option == "b": s_store("blacksmith")
        elif option == "a": s_store("arcanist")
        elif option == "f": s_market()
        elif option == "B": break
        if returnTo(): break

def s_tavern():
    while 1:
        clear()
        print("\n -= Tavern =-")

        price = 5 + player.level * 2

        print(f'\n Price to rest: {c("yellow")}● {reset}{price}.')

        options(["Rest", "Drink", c("dark gray") + "Quest", c("dark gray") + "Gamble"])
        option = command(False, "alphabetic", options = "rd")

        if option == "r":
            if player.gold >= price:
                player.gold -= price
                player.hp = player.stats["max hp"]
                player.mp = player.stats["max mp"]
                player.addPassive(newPassive("Well Rested"))
                player.updateStats()
                print(f'\n You feel well rested.')
                pressEnter()
            else:
                print(f'\n {c("yellow")}Barkeep:{reset} You don\'t have enough coin to stay.')
                pressEnter()
        elif option == "d": s_store("tavern")
        elif option == "B": break
        if returnTo(): break

def s_store(store):
    page = 1
    while 1:
        clear()
        storeData = loadStore(player.location, store)
        
        itemList = [newItem(item) for item in storeData["inventory"]]
        next = False if len(itemList) < (page+1)*10 else True
        previous = False if page == 1 else True

        print(f'\n -= {store.capitalize()} =-')
        printEvalText(storeData["description"])
        print("")
        displayPlayerGold()
        print("")

        for i in range(-10 + 10*page, 10*page if 10*page < len(itemList) else len(itemList)):
            print(f' {i}) {displayItem(itemList[i]["name"], itemList[i]["rarity"], 1 if itemList[i]["type"] in stackableItems else 0)} {c("yellow")}●{reset} {itemList[i]["value"]}')

        if len(itemList) == 0: print(" " + c("dark gray") + "- Empty -" + reset)

        options((["Next"] if next else []) + (["Previous"] if previous else []))
        option = command(False, "optionumeric", options = ("n" if next else "") + ("p" if previous else "") + "".join(tuple(map(str, range(0, len(itemList))))))

        if option in tuple(map(str, range(0, len(itemList)))): s_purchase(itemList[int(option)])
        elif option == "n" and next: page += 1
        elif option == "p" and previous: page -= 1
        elif option == "B": break
        if returnTo(): break

def s_purchase(item):
    while 1:
        clear()
        player.updateStats()

        print(f'\n -= Purchase {item["type"].capitalize()} =-')

        displayItemStats(item)
        print(f'\n Cost: {c("yellow")}● {reset}{item["value"]}')
        displayPlayerGold()

        print(f'\n Type the quantity of items to be purchased.')

        option = command(True, "numeric")

        if option in tuple(map(str, range(1, player.gold // item["value"] + 1))):
            if player.gold // item["value"] >= 1:
                player.addItem(item, int(option))
                player.gold -= item["value"] * int(option)
                print(f'\n {displayItem(item["name"], item["rarity"], int(option))} added to your inventory.')
            else: print(f'\n {c("light red")}You don\'t have enough gold to buy {item["name"]} x{int(option)}.')
            pressEnter()
            break
        elif option == "B": break
        if returnTo(): break

def s_market():
    page = 1
    while 1:
        clear()
        print("\n -= Flea Market =- \n")

        for i in range(-10 + 10*page, 10*page if 10*page < len(player.inventory) else len(player.inventory)):
            print(f' {str(i)[:-1]}({str(i)[-1]}) {displayItem(player.inventory[i][0]["name"], player.inventory[i][0]["rarity"], (player.inventory[i][1] if player.inventory[i][0]["type"] in stackableItems else 0))}')

        if len(player.inventory) == 0:
            print(" " + c("dark gray") + "- Empty -" + reset)

        next = False if len(player.inventory) < page*10 + 1 else True
        previous = False if page == 1 else True

        options((["Next"] if next else []) + (["Previous"] if previous else []))
        option = command(False, "optionumeric", options = ("n" if next else "") + ("p" if previous else "") + "".join(tuple(map(str, range(0, len(player.inventory))))))

        if option in tuple(map(str, range(0, len(player.inventory)))):
            s_sell(player.inventory[int(option) + (page-1) * 10][0])
        elif option == "n" and next: page += 1
        elif option == "p" and previous: page -= 1
        elif option == "B": break
        if returnTo(): return

def s_sell(item):
    while 1:
        clear()
        player.updateStats()

        print(f'\n -= Sell {item["type"].capitalize()} =-')

        displayItemStats(item)
        print(f'\n Sell value: {c("yellow")}● {reset}{round(item["value"] * 0.66)}')

        print(f'\n Type the quantity of items to be sold ({player.numOfItems(item["name"])} available).')

        option = command(True, "numeric")

        if option in tuple(map(str, range(1, player.numOfItems(item["name"]) + 1))):
            player.removeItem(item, int(option))
            player.gold += round(item["value"] * 0.66) * int(option)
            print(f'\n Sold {displayItem(item["name"], item["rarity"], 0 if int(option) == 1 and item["type"] == "equipment" else int(option))}.')
            pressEnter()
            break
        elif option == "B": break
        else:
            print("\n You cannot sell that many.")
            pressEnter()
        if returnTo(): return


# :::::  :   :   :::   :::::   :::   :::::  :::::  :::::  :::::
# :      :   :  :   :  :   :  :   :  :        :    :      :   :
# :      :::::  :::::  ::::   :::::  :        :    :::    ::::
# :      :   :  :   :  :   :  :   :  :        :    :      :   :
# :::::  :   :  :   :  :   :  :   :  :::::    :    :::::  :   :


def s_character():
    while 1:
        clear()

        print("\n -= Character =-")
        displayPlayerStats()

        options(["Inventory", "Equipment", "Crafting", "Stats"])
        option = command(options = "iecs")

        if option == "i": s_inventory()
        elif option == "e": s_equipment()
        elif option == "c": s_crafting()
        elif option == "s": s_stats()
        elif option == "B": break
        if returnTo(): break

def s_inventory():
    page = 1
    while 1:
        clear()

        print("\n -= Inventory =-\n")

        for i in range(-10 + 10*page, 10*page if 10*page < len(player.inventory) else len(player.inventory)):
            print(f' {str(i)[:-1]}({str(i)[-1]}) {displayItem(player.inventory[i][0]["name"], player.inventory[i][0]["rarity"], (player.inventory[i][1] if player.inventory[i][0]["type"] in stackableItems else 0))}')

        if len(player.inventory) == 0:
            print(" " + c("dark gray") + "- Empty -" + reset)

        next = len(player.inventory) > page*10 + 1
        previous = page != 1

        options((["Next"] if next else []) + (["Previous"] if previous else []))
        option = command(False, "optionumeric", options = ("n" if next else "") + ("p" if previous else "") + "".join(tuple(map(str, range(0, len(player.inventory))))))

        if option in tuple(map(str, range(0, len(player.inventory)))):
            s_inspect(player.inventory[int(option) + (page-1) * 10][0], False)
        elif option == "n" and next: page += 1
        elif option == "p" and previous: page -= 1
        elif option == "B": break
        if returnTo(): return

def s_equipment():
    while 1:
        clear()

        print("\n -= Equipment =-")
        print("\n Type the number of the item you wish to inspect.\n")

        for i in range(len(slotList)):
            if player.equipment[slotList[i]] != "": print(f' {i}) {displayItem(player.equipment[slotList[i]]["name"], player.equipment[slotList[i]]["rarity"])}')
            else: print(f' {i}) {c("dark gray")} - Empty -{reset}')

        option = command(False, "numeric", options = "".join(tuple(map(str, range(0, len(slotList))))))

        if option in tuple(map(str, range(0, len(slotList)))) and player.equipment[slotList[int(option)]] != "":
            s_inspect(player.equipment[slotList[int(option)]], True)
        elif option == "B": break

def s_inspect(item, equipped):
    while 1:
        clear()
        player.updateStats()

        print(f'\n -= Inspect {item["type"].capitalize()} =-')

        displayItemStats(item)
        print(f'\n Sell Price: {c("yellow")}● {reset}{item["value"]}')

        if item["type"] == "equipment":
            options(["Unequip"] if equipped else ["Equip", "Discard"])
            option = command(False, "alphabetic", options = "u" if equipped else "ed")
        elif item["type"] == "consumable":
            options((["Use"] if item["target"] == "self" else []) + ["Discard"])
            option = command(False, "alphabetic", options = ("u" if item["target"] == "self" else "") + "d")
        else:
            options(["Discard"])
            option = command(False, "alphabetic", options = "d")

        if option == "u" and item["type"] == "equipment":
            player.unequip(item["slot"])
            break
        elif option == "e" and item["type"] == "equipment":
            player.equip(item)
            break
        elif item["type"] == "consumable" and option == "u" and item["target"] == "self":
            text = []
            for effect in item["effect"]:
                if "passive" in effect:
                    if type(effect["passive"]) is list: passive = [newPassive(p) for p in effect["passive"]]
                    else: passive = newPassive(effect["passive"])
                else:
                    passive = False
                tempText, playerDamage = player.defend(newPassive(effect["name"]) if effect["type"] == "passive" else effect, passive=passive)
                text.append(tempText)
            text[0] = f'\n {player.name} {item["useVerb"]} {displayItem(item["name"], item["rarity"], 1)}, ' + text[0]
            for line in text:
                print(evalText(line))
            pressEnter()
            player.removeItem(item)
            if player.numOfItems(item["name"]) <= 0: break
        elif option == "d":
            if player.numOfItems(item["name"]) > 1:
                while 1:
                    clear()
                    print("\n -= Quantity =-")
                    print(f'\n Type the quantity to discard (1-{player.numOfItems(item["name"])})')

                    option = command(True, "numeric")

                    if option == "B": break
                    elif option in tuple(map(str, range(1, player.numOfItems(item["name"])+1))):
                        player.removeItem(item, int(option))
                        return
            else:
                player.removeItem(item)
                break
        elif option == "B": break
        if returnTo(): break

def s_crafting():
    page = 1
    while 1:
        clear()
        
        print("\n -= Crafting =-\n")
        
        unlockedRecipes = [recipe for recipe in recipes if any(player.numOfItems(item[0]) >= 1 for item in recipe["ingredients"])]
        
        for i in range(-10 + 10*page, 10*page if 10*page < len(unlockedRecipes) else len(unlockedRecipes)):
            print(f' {str(i)[:-1]}({str(i)[-1]}) {displayItem(items[unlockedRecipes[i]["result"]]["name"], items[unlockedRecipes[i]["result"]]["rarity"], (unlockedRecipes[i]["quantity"] if items[unlockedRecipes[i]["result"]]["type"] in stackableItems else 0))}')
        
        if len(unlockedRecipes) == 0:
            print(" " + c("dark gray") + "- No craftable recipes -" + reset)
        
        next = False if len(unlockedRecipes) < page*10 + 1 else True
        previous = False if page == 1 else True

        options((["Next"] if next else []) + (["Previous"] if previous else []))
        option = command(False, "optionumeric", options = ("n" if next else "") + ("p" if previous else "") + "".join(tuple(map(str, range(0, len(unlockedRecipes))))))

        if option in tuple(map(str, range(0, len(unlockedRecipes)))):
            s_craft(unlockedRecipes[int(option) + (page-1) * 10])
        elif option == "n" and next: page += 1
        elif option == "p" and previous: page -= 1
        elif option == "B": break
        if returnTo(): return

def s_craft(recipe):
    while 1:
        clear()
        player.updateStats()

        item = newItem(recipe["result"])
        print(f'\n -= Inspect {item["type"].capitalize()} =-')

        displayItemStats(item)
        print(f'\n Sell Price: {c("yellow")}● {reset}{item["value"]}')
        
        craftable = True
        numCraftable = 0
        print(f'\n Requires:\n')
        for i in range(len(recipe["ingredients"])):
            playerIngredientCount = player.numOfItems(recipe["ingredients"][i][0])
            recipeIngredientRequirement = recipe["ingredients"][i][1]
            if playerIngredientCount < recipeIngredientRequirement:
                craftable = False
            elif playerIngredientCount // recipeIngredientRequirement < numCraftable:
                numCraftable = playerIngredientCount // recipeIngredientRequirement
            print(f' {recipeIngredientRequirement}x {displayItem(recipe["ingredients"][i][0], items[recipe["ingredients"][i][0]]["rarity"], 0)} ({playerIngredientCount}/{recipeIngredientRequirement})')
        
        if item["type"] == "equipment" and craftable: numCraftable = 1
        print(f'\n Type the quantity of items to be crafted ({numCraftable} craftable).')
        option = command(True, "numeric")
        
        if option in "".join(tuple(map(str, range(0, numCraftable + 1)))):
            for i in recipe["ingredients"]:
                player.removeItem(newItem(i[0]), i[1] * int(option))
            player.addItem(item, recipe["quantity"] * int(option))
            print(f'\n Crafted {displayItem(item["name"], item["rarity"], (recipe["quantity"] if item["type"] in stackableItems else 0))}!')
            pressEnter()
            break
        elif option == "B": break
        else:
            print("\n You cannot craft that many.")
            pressEnter()
        if returnTo(): return

def s_stats():
    page = 1
    player.updateStats()
    while 1:
        clear()

        print("\n -= Player Stats =-\m")

        stats = player.stats.copy()
        stats.pop("attack")
        stats.pop("max hp")
        stats.pop("max mp")
        statNamePad = len(max(player.stats, key=len)) + 1
        statValuePad = len(max([str(player.stats[stat]) for stat in stats], key=len))

        displayPlayerTitle()
        displayPlayerHP()
        displayPlayerMP()
        displayPlayerXP()
        displayPlayerGold()
        print("")
        print(f' {"Attack".ljust(statNamePad)}: {(str(player.stats["attack"][0]) + " - " + str(player.stats["attack"][1])).ljust(statValuePad)}')

        for stat in stats:
            print(f' {stat.capitalize().ljust(statNamePad)}: {str(player.stats[stat]).ljust(statValuePad)} ({"+" if player.baseStats[stat] <= player.stats[stat] else ""}{player.stats[stat] - player.baseStats[stat]})')

        print("\n -= Player Passives =-\n")

        for i in range(-10 + 10*page, 10*page if 10*page < len(player.passives) else len(player.passives)):
            print(f' {str(i)[:-1]}({str(i)[-1]}) {c("light green" if player.passives[i]["buff"] else "light red")}{player.passives[i]["name"]}{reset} ({player.passives[i]["turns"]})')
        
        if len(player.passives) == 0:
            print(" " + c("dark gray") + "- Empty -" + reset)
        
        next = len(player.passives) > page*10 + 1
        previous = page != 1
        
        options((["Next"] if next else []) + (["Previous"] if previous else []))
        option = command(False, "optionumeric", options = ("n" if next else "") + ("p" if previous else "") + "".join(tuple(map(str, range(0, len(player.passives))))))
        
        if option in tuple(map(str, range(0, len(player.passives)))):
            clear()
            print(f'\n -= Inspecting {c("light green" if player.passives[int(option) + (page-1) * 10]["buff"] else "light red")}{player.passives[int(option) + (page-1) * 10]["name"]}{reset} =-')
            print("  " + player.passives[int(option) + (page-1) * 10]["description"])
            print("\n Effects:")
            e = newPassive(player.passives[int(option) + (page-1) * 10]["name"])["effect"]
            effects = {}
            for effect in e:
                effects.update({effect["type"]: effect})
            displayEffect(effects)
            pressEnter()
        elif option == "n" and next: page += 1
        elif option == "p" and previous: page -= 1
        elif option == "B": break
        if returnTo(): break


# :::::   :::   :   :  :::::       :         :::::  :   :  :::::  :::::
# :      :   :  :   :  :          : : :      :   :  :   :    :      :
# :::::  :::::   : :   :::         :: :      :   :  :   :    :      :
#     :  :   :   : :   :          :  :       :  :   :   :    :      :
# :::::  :   :    :    :::::       :: :      ::: :  :::::  :::::    :


def s_save():
    global saves
    page = 1
    while 1:
        clear()

        print("\n -= Save =-\n")

        for i in range(-10 + 10*page, 10*page if 10*page < len(saves) else len(saves)):
            print(f' {i}) {saves[i][1]} | {saves[i][0].name} [Lvl {saves[i][0].level}]')

        if len(saves) == 0:
            print(" " + c("dark gray") + "- Empty -" + reset)

        options(["Create", "Delete"])
        option = command(False, "optionumeric", options = "cd" + "".join(tuple(map(str, range(0, len(saves))))))

        if option in tuple(map(str, range(0, len(saves)))):
            pickle.dump(player, open("data\\saves\\" + saves[int(option)][1], "wb"))
            saves = [[pickle.load(open("data\\saves\\" + file, "rb")), file] for file in os.listdir("data\\saves") if not file.endswith(".txt")]
            print("\n File saved successfully!")
            pressEnter()
            break
        elif option == "c": s_create()
        elif option == "d": s_delete()
        elif option == "B": break
        if returnTo(): break

def s_create():
    global saves
    while 1:
        clear()

        print("\n -= New Save =-")
        print("\n Saves must contain only characters alphanumeric characters and spaces.")
        print(" Saves must be 2+ characters long")
        print("\n Current Saves:")

        for save in saves:
            print(f' - {save[1]} | {save[0].name} [Lvl {save[0].level}]')

        print("\n Please type the new file name.")
        option = command(True, "alphanumeric")

        if option == "B": break
        elif not re.match("[\w\s]", option) or len(option) < 2:
            print("\n Your name cannot be \"" + option + "\".")
            pressEnter()
        else:
            pickle.dump(player, open("data\\saves\\" + option.capitalize(), "wb"))
            saves = [[pickle.load(open("data\\saves\\" + file, "rb")), file] for file in os.listdir("data\\saves") if not file.endswith(".txt")]
            print("\n File saved successfully!")
            pressEnter()
            break
        if returnTo(): break

def s_delete():
    global saves
    while 1:
        clear()

        print("\n -= Delete =-")

        if len(saves) > 0: print("")
        else: print("\n " + c("dark gray") + "- Empty -" + reset)

        for i in range(len(saves)):
            print(f' {i}) {saves[i][1]} | {saves[i][0].name} [Lvl {saves[i][0].level}]')

        option = command(False, "numeric", options = "".join(tuple(map(str, range(0, len(saves))))))

        if option == "B": break
        elif option in tuple(map(str, range(0, len(saves)))):
            os.remove("data\\saves\\" + saves[int(option)][1])
            saves = [[pickle.load(open("data\\saves\\" + file, "rb")), file] for file in os.listdir("data\\saves") if not file.endswith(".txt")]
            print("\n File deleted successfully!")
            pressEnter()
            break
        if returnTo(): break

def s_quit():
    while 1:
        clear()

        print("\n -= Quit =-")
        print("\n Are you sure you want to quit without saving?")

        options(["Yes"])
        option = command(options = "y")

        if option == "y": sys.exit()
        elif option == "B": return
        if returnTo(): break





# :::::::::::::::::::..   .-:.     ::-.   :\     .,::::::    .,::      .:  .,-:::::  .,::::::  ::::::::::. ::::::::::::
# ;;;;;;;;'''';;;;``;;;;   ';;.   ;;;;'   .;;'   ;;;;''''    `;;;,  .,;; ,;;;'````'  ;;;;''''   `;;;```.;;;;;;;;;;;''''
#      [[      [[[,/[[['     '[[,[[['    ([__     [[cccc       '[[,,[['  [[[          [[cccc     `]]nnn]]'      [[     
#      $$      $$$$$$c         c$$"      c$""     $$""""        Y$$$P    $$$          $$""""      $$$""         $$     
#      88,     888b "88bo,   ,8P"`       "Yo,oP   888oo,__    oP"``"Yo,  `88bo,__,o,  888oo,__    888o          88,    
#      MMM     MMMM   "W"   mM"             "M,   """"YUMMM,m"       "Mm,  "YUMMMMMP" """"YUMMM   YMMMb         MMM    





try:
    if __name__ == "__main__":
        os.system("mode con: cols=150 lines=40") # Leaves 28 lines of space if there's a header and 3 options
        os.system("title=Magyka")

        print("\n Loading...")

        def blockAltEnter():
            keyboard.press_and_release("f11")

        keyboard.press_and_release("windows + up")
        keyboard.block_key("f11")
        keyboard.add_hotkey("alt + enter", blockAltEnter)

        saves = [[pickle.load(open("data\\saves\\" + file, "rb")), file] for file in os.listdir("data\\saves") if not file.endswith(".txt")]

        def newItem(name):
            return copy.deepcopy(items[name])

        def newEnemy(name):
            return Enemy(enemies[name])
        
        def newPassive(name):
            return copy.deepcopy(passives[name])
        
        def loadStore(location, storeType):
            return stores[location][storeType]
        
        def loadEncounter(location, area):
            return [[enemy[0]*2, newEnemy(enemy[1])] for enemy in encounters[location][area]]
    
        with open("data\\items.json", "r") as itemFile:
            items = json.load(itemFile)
        items = {item["name"]: item for item in items}

        with open("data\\enemies.json", "r") as enemyFile:
            enemies = json.load(enemyFile)
        enemies = {enemy["name"]: enemy for enemy in enemies}
        
        with open("data\\encounters.json", "r") as encounterFile:
            encounters = json.load(encounterFile)
        
        with open("data\\recipes.json", "r") as recipeFile:
            recipes = json.load(recipeFile)
        
        with open("data\\stores.json", "r") as storeFile:
            stores = json.load(storeFile)
        
        with open("data\\passives.json", "r") as passiveFile:
            passives = json.load(passiveFile)
        passives = {passive["name"]: passive for passive in passives}
        
        with open("data\\settings.json", "r+") as settingsFile:
            settings = json.load(settingsFile)
        
        if settings["fullscreen"]: fullscreen()
        
        player = Player({"weapon": newItem("Tarnished Sword"),"tome": "","head": "","chest": newItem("Patched Shirt"),"legs": newItem("Patched Jeans"),"feet": "","accessory": ""})
        s_mainMenu()
except Exception as err:
    # Get Exception
    errType, errValue, errTraceback = sys.exc_info()
    trace_back = traceback.extract_tb(errTraceback)
    stackTrace = list()
    for trace in trace_back:
        stackTrace.append(f'{trace[2]} [{trace[1]}]: {trace[3]}')
    print("\nException at " + time.ctime(time.time()) + "\n " + str(errType.__name__) + ": " + str(errValue) + "\n " + str(stackTrace[-1]) + "\n " + str(stackTrace[:-2]))

    # Restart Program
    pressEnter()
    if settings["fullscreen"]: fullscreen()
    os.execv(sys.executable, ['python'] + sys.argv)