# TODO
# Add dungeons as locations, instead of hunting grounds
# Add tavern giving randomly generated quests
# Add search feature, and make randomly generated loot
# Add loot bags, with loot that functions the same as enemy drops
# Add different types of camp locations, e.g. one without a town but something else
# Add viewing of ASCII map segments
# Add ASCII map movement
# Add support for sub maps
# Add json file for world to sub, vice versa, and sub to sub teleportation





# ::::::.    :::.::::::::::::::::::  :::.      :::     ::::::::::::.,::::::  
# ;;;`;;;;,  `;;;;;;;;;;;;;;'''';;;  ;;`;;     ;;;     ;;;'`````;;;;;;;''''  
# [[[  [[[[[. '[[[[[     [[     [[[ ,[[ '[[,   [[[     [[[    .n[[' [[cccc   
# $$$  $$$ "Y$c$$$$$     $$     $$$c$$$cc$$$c  $$'     $$$  ,$$P"   $$""""   
# 888  888    Y88888     88,    888 888   888,o88oo,.__888,888bo,_  888oo,__ 
# MMM  MMM     YMMMM     MMM    MMM YMM   ""` """"YUMMMMMM `""*UMM  """"YUMMM


# Os specific module importing

from data.Globals import *
if system == "Windows": import win32gui, msvcrt
else: import tty, termios, select

print("\n Loading...")

# Crossplatform module importing

import copy
import inspect
import json
import numpy
import math
import os
import pickle
import random
import re
import sqlite3
import string
import sys
import time
import traceback

# Modules and classes

from data.Effect import *
from data.Entity import *
from data.Item import *
from data.mapToAscii import *





# .::::::' ...    ::::::.    :::.  .,-:::::  :::::::::::::::    ...     :::.    :::. .::::::. 
# ;;;''''  ;;     ;;;`;;;;,  `;;;,;;;'````'  ;;;;;;;;'''';;; .;;;;;;;.  `;;;;,  `;;;;;;`    ` 
# [[[,,== [['     [[[  [[[[[. '[[[[[              [[     [[[,[[     \[[,  [[[[[. '[['[==/[[[[,
# `$$$"`` $$      $$$  $$$ "Y$c$$$$$              $$     $$$$$$,     $$$  $$$ "Y$c$$  '''    $
#  888    88    .d888  888    Y88`88bo,__,o,      88,    888"888,_ _,88P  888    Y88 88b    dP
#  "MM,    "YmmMMMM""  MMM     YM  "YUMMMMMP"     MMM    MMM  "YMMMMMP"   MMM     YM  "YMmMY" 


# Item modification

def enchantEquipment(item, enchantment):
    if enchantment == None: return item
    
    # Looping through item enchantments to combine the enchantment or check for duplicates
    enchantmentFound = False
    for i in range(len(item["enchantments"])):
        if item["enchantments"][i]["name"] == enchantment["name"]:
            enchantmentFound = True
            if item["enchantments"][i]["level"] == enchantment["level"] and item["enchantments"][i]["level"] < item["enchantments"][i]["maxLevel"]:
                item["enchantments"][i] = newEnchantment(item["enchantments"][i]["real name"], item["enchantments"][i]["tier"], item["enchantments"][i]["level"] + 1)
            elif item["enchantments"][i]["level"] < enchantment["level"]:
                item["enchantments"][i]["level"] = enchantment["level"]
            pressEnter()
            break
    if not enchantmentFound: item["enchantments"].append(enchantment)
    
    return updateEquipment(item)


def modifyEquipment(item, modifier):
    if modifier == None: return item

    item["modifier"] = modifier
    return updateEquipment(item)


def updateEquipment(item):
    oldItem = item
    item = copy.deepcopy(oldItem)
    item["effect"], item["tags"], item["value"] = copy.deepcopy(item["base effect"]), copy.deepcopy(item["base tags"]), item["base value"]
    
    # Getting the names of all enchantment and modifier stats
    try:
        statNames = []
        if item["modifier"]["effect"] != []: statNames = [effect["type"] for effect in item["modifier"]["effect"]]
        if item["enchantments"] != []: statNames += [effect["type"] for effect in [enchantment["effect"] for enchantment in item["enchantments"]][0]]
        effects, tags, values = [], [], []
        
        # Adding all enchantment and modifier effects, tags, and values to their respective lists
        values.append(item["modifier"]["value"])
        
        tags += item["modifier"]["tags"]
        for effect in item["modifier"]["effect"]:
            if effect["type"] in player.stats: effects.append(effect)
        
        for enchantment in item["enchantments"]:
            tags += enchantment["tags"]
            values.append(enchantment["value"])
            for effect in enchantment["effect"]:
                if effect["type"] in player.stats: effects.append(effect)
        
        # Sorting through tags to remove duplicate and deal with passive tags
        for tag in tags:
            name = tag.split(":")[0]
            try: value = tag.split(":")[1]
            except: value = False
            tagFound = False
            for t in item["tags"]:
                if name == t.split(":")[0]:
                    if len(t.split(":")) == 1 or not value:
                        tagFound = True
                        break
                    else:
                        tagFound = True
                        item["tags"].append(name + ":" + str(int(value) + int(t.split(":")[1])))
                        item["tags"].remove(t)
            if not tagFound:
                if name == "passive":
                    if "passive" in item["effect"][0]: item["effect"][0]["passive"].append(value)
                    else: item["effect"][0].update({"passive": [value]})
                else: item["tags"].append(tag)
        
        # Calculating the value of the item from the values in values
        for value in values:
            if value[0] == "+": item["value"] += int(value[1:])
            elif value[0] == "-": item["value"] -= int(value[1:])
            elif value[0] == "*": item["value"] = round(float(value[1:]) * item["value"])

        # Adding the stats in statNames that the item currently doesn't have
        for statName in statNames:
            statFound = False
            for effect in item["effect"]:
                if statName == effect["type"]:
                    statNames = [statName for statName in statNames if statName != effect["type"]]
                    statFound = True
                    break
            if not statFound: item["effect"].append({"type": statName, "value": 0})

        # Adding every effect provided by enchantments and modifiers to the item
        for e in effects:
            for effect in item["effect"]:
                if e["type"] == effect["type"]:
                    if effect["type"] == "attack":
                        for i in range(2):
                            if "*" in e: effect["value"][i] = round(effect["value"][i] * ((e["value"] / 100) + 1))
                            else: effect["value"][i] += e["value"]
                    else:
                        if "*" in effect: round(effect["value"] * ((e["value"] / 100) + 1))
                        else: effect["value"] += e["value"]
        return item
    except:
        printError()
        pressEnter()
        return oldItem


# Non-input functions

def clear():
    os.system(clearCommand)
    global screen
    screen = inspect.stack()[1][3]
    setCursorVisible(False)


def exitGame():
    clear()
    if system != "Windows": termios.tcsetattr(sys.stdin, termios.TCSADRAIN, orig_settings)
    sys.exit()


# Formatting

def openText(path):
    # Open file as string
    return open(path, "r").read()


def evalText(text):
    # Evaluate a string as an fstring
    return eval(f'f"""{text}"""')


def openEvalText(path):
    # Open a file as string and evaluate it as an fstring
    return evalText(openText(path))


def openTextAsList(path, splitter = "|"):
    # Open file as list of strings
    return openText(path).split(splitter)


def evalTextAsList(path, splitter = "|"):
    # Open file as list of strings and evaluate each string as an fstring
    return [eval(subText) for subText in openTextAsList(path, splitter)]


def dictFactory(cursor, row):
    # Converts sqlite return value into a dictionary with column names as keys
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


# Input

def get_key():
    # Get key as soon as one is available
    key = ""
    if system == "Windows":
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
        key = msvcrt.getch().decode("utf-8")
        if key == "K": return "left"
        elif key == "M": return "right"
        elif key == "H": return "up"
        else: return "down"
    else: return key


def wait_to_key(key):
    # Blocks code until specified key is pressed
    while 1:
        time.sleep(0.05)
        if get_key() == key: break


def command(input = False, mode="alphabetic", back=True, silent=False, lower=True, options="", prompt="", horizontal=False):
    # Printing prompt and help tooltip
    if input:
        if mode == "command": print(f'\n{c("option")} Console >| {reset}', end = "")
        else: print(f'\n{c("option")} > {reset}', end = "")
        setCursorVisible(True)
    elif silent: helpText = ""
    elif mode == "none": helpText = "- Press ESC to go back."
    elif mode == "alphabetic": helpText = "- Press a letter" + (", or ESC to go back." if back else ".")
    elif mode == "numeric": helpText = "- Press a number, or ESC to go back."
    elif mode == "optionumeric": helpText = "- Press a number or letter, or ESC to go back."

    if not input:
        if horizontal: print("\n" + helpText.center(os.get_terminal_size()[0]))
        else: print("\n  " + helpText)


    # Input handling
    a = prompt
    loc = len(prompt)
    print(a, end = "")
    sys.stdout.flush()
    terminalSize = os.get_terminal_size()
    historyPosition = len(commandHistory)
    while 1:
        time.sleep(0.05)
        key = get_key()
        if terminalSize != os.get_terminal_size(): return "D"
        # Looking for single character keys
        if len(key) == 1 and (mode in ("command", "all")) or (re.match("[0-9]", key) and mode in ("numeric", "optionumeric", "alphanumeric")) or (re.match("[A-Za-z\_\s\/]", key) and mode in ("alphabetic", "optionumeric", "alphanumeric")):
            if input:
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
        if key == "space" and input:
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
        if key == "enter" and input:
            print("")
            break
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
        # Command history
        if (key == "up" or key == "down") and mode == "command":
            print(" "*(len(a) - loc), end="")
            print("\b \b"*len(a), end="")
            sys.stdout.flush()
            if historyPosition <= 0 and key == "up": historyPosition = 1
            if historyPosition > len(commandHistory) and key == "down": len(commandHistory)
            historyPosition += -1 if key == "up" else 1
            if historyPosition < len(commandHistory):
                print(commandHistory[historyPosition], end="")
                sys.stdout.flush()
                a = commandHistory[historyPosition]
                loc = len(a)
            else:
                a = ""
                loc = 1
    setCursorVisible(False)

    # Returning input value
    if a == "": return ""
    if not mode == "command": return (str.lower(a).strip() if lower else a.strip())

    # Running command from console input
    devCommand(a)
    return "D"


def devCommand(a):
    global commandHistory
    commandHistory.append(a)

    a1 = a.split(" ", 1)
    a2 = a.split(" ", 2)
    a3 = a.split(" ", 3)

    if a1[0] == "fight":
        s_battle(newEnemy(a1[1]))
    elif a == "s":
        player.name = "Vincent"
        s_camp()
    elif a == "d":
        player.gold = 999999999
        player.name = "Dev"
        s_camp()
    elif a == "restart":
        clear()
        os.execv(sys.executable, ['python'] + sys.argv)
    elif a == "reload map":
        global worldMap
        worldMap = displayImage()
        return
    
    try:
        if a1[0] == "equip":
            if a1[1] in items:
                if player.equipment[items[a1[1]]["slot"]] != "": player.unequip(items[a1[1]]["slot"])
                player.equip(newItem(a1[1]))
        elif a1[0] == "exec":
            exec(a1[1])
        elif a1[0] == "execp":
            print("\n " + str(eval(a1[1])))
            pressEnter()
        elif a1[0] == "finish":
            for i in range(len(player.quests)):
                if player.quests[i]["name"] == a1[1]:
                    player.finishQuest(i)
        elif a == "flee":
            returnToScreen("s_explore")
        elif a1[0] == "give":
            a1s = a1[1].split(", ")
            if a1s[0] == "dev":
                session = sqlite3.connect("data/data.db")
                session.row_factory = dictFactory
                devItems = [item["name"] for item in session.cursor().execute("select * from items where name like ':%'").fetchall()]
                for item in devItems:
                    player.addItem(newItem(item))
                session.close()
            elif a1s[0] == "all":
                for item in items:
                    player.addItem(newItem(item), (int(a1s[1]) if len(a1s) == 2 else 1))
            elif a1s[0] in items:
                player.addItem(newItem(a1s[0]), (int(a1s[1]) if len(a1s) == 2 else 1))
        elif a2[0] == "enchant":
            a2s = a2[2].split(", ")
            player.equipment[a2[1]] = enchantEquipment(player.equipment[a2[1]], newEnchantment(a2s[0], int(a2s[1]), int(a2s[2])))
            player.updateStats()
        elif a2[0] == "modify":
            player.equipment[a2[1]] = modifyEquipment(player.equipment[a2[1]], newModifier(a2[2]))
        elif a1[0] == "gold":
            player.gold += int(a1[1])
        elif a1[0] == "name":
            player.name = a1[1].strip()
        elif a == "quit":
            exitGame()
        elif a == "clear passives":
            player.passives = []
            player.updateStats()
        elif a == "clear inventory":
            player.inventory = []
        elif a == "clear equipment":
            for slot in player.equipment:
                player.equipment[slot] == ""
        elif a == "restore":
            player.hp, player.mp = player.stats["max hp"], player.stats["max mp"]
        elif a1[0] == "xp":
            player.xp += int(a1[1])
        else:
            print(c("light red") + "\n That's not a command, stupid." + reset)
            pressEnter()
    except Exception as err:
        printError()
        pressEnter()


def pressEnter(prompt = f'{c("option")}[Press Enter]', horizontal=False):
    setCursorVisible(False)
    if horizontal: print("\n" + prompt.center(os.get_terminal_size()[0] + prompt.count("\x1b") * 9) + reset)
    else: print("\n " + prompt + reset)
    wait_to_key("enter")
    setCursorVisible(True)


def options(names, horizontal=False):
    if len(names) > 0: print("")
    if horizontal:
        text = ""
        for i in range(len(names)):
            text += f'{c("option") + c("dark gray", True)}[{names[i][11 if ";" in names[i] else 0]}]{reset} {names[i]}'
            if i < len(names)-1:
                text += "       " if os.get_terminal_size()[0] > 74 else "  "
        print(text.center(os.get_terminal_size()[0] + text.count("\x1b") * 9))
    else:
        for i in range(len(names)):
            print(f' {c("option") + c("dark gray", True)}[{names[i][11 if ";" in names[i] else 0]}]{reset} {names[i]}')
            if i < len(names)-1:
                print(f' {c("option") + c("dark gray", True)} |{reset}')
    print(reset, end="")


# Menu escaping

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


# Text printing

def write(text, speed = textSpeed):
    i = 0
    delay = speed
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
        if get_key() == "enter": delay = 0
        sys.stdout.flush()
        i += 1
    print("\n")


def displayItem(name, rarity, quantity = 0):
    amt = ("" if quantity == 0 else " x" + str(quantity))
    if rarity == "garbage": return c("light red") + name + reset + amt
    if rarity == "common": return c("lightish gray") + name + reset + amt
    if rarity == "uncommon": return c("lightish green") + name + reset + amt
    if rarity == "rare": return c("light blue") + name + reset + amt
    if rarity == "epic": return c("light purple") + name + reset + amt
    if rarity == "legendary": return c("light orange") + name + reset + amt
    if rarity == "mythical": return c("lightish red") + name + reset + amt


def displayEffect(effects, notes=False, extraSpace=False):
    begin = " "
    noteBegin = " - "
    if notes: begin, noteBegin = "  - ", "  - "
    if extraSpace: begin, noteBegin = "   - ", "   - "
    if not notes: print("")
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
        print(f'{begin}Damage: {damage}.\n')
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
        print(f'{begin}Heals {heal}')
        if effect in ("hp", "all"): print(" " + returnHpBar(player) + "\n")
        if effect in ("mp", "all"): print(" " + returnHpBar(player) + "\n")
    if "attack" in effects:
        if type(effects["attack"]["value"]) is list: print(f'{begin}Damage: {c("red")}{effects["attack"]["value"][0]} - {effects["attack"]["value"][1]} ♥{reset}.\n')
        else:
            if "*" in effects["attack"]:
                print(f'{begin}{abs(effects["attack"]["value"])}% {"Increased" if effects["attack"]["value"] > 0 else "Decreased"} Attack')
            else:
                print(f'{begin}{"+" if effects["attack"]["value"] > 0 else ""}{effects["attack"]["value"]} Attack')


def displayStats(effects, notes=False, extraSpace=False):
    begin = " "
    noteBegin = " - "
    if notes: begin, noteBegin = "  - ", "  - "
    if extraSpace: begin, noteBegin = "   - ", "   - "
    for stat in ("max hp", "max mp", "armor", "strength", "intelligence", "vitality"):
        if stat in effects:
            if stat == "max hp":
                color, character = c("red"), " ♥"
            elif stat == "max mp":
                color, character = c("blue"), " ♦"
            else:
                color, character = "", ""
            
            if "*" in effects[stat]:
                print(f'{noteBegin}{abs(effects[stat]["value"])}% {"Increased" if effects[stat]["value"] > 0 else "Decreased"} {color}{stat.capitalize()}{character}{reset}')
            else:
                print(f'{noteBegin}{"+" if effects[stat]["value"] > 0 else ""}{effects[stat]["value"]} {color}{stat.capitalize()}{character}{reset}')
    for stat in ("crit", "hit", "dodge"):
        if stat in effects: print(f'{noteBegin}{abs(effects[stat]["value"])}% {"Increased" if effects[stat]["value"] > 0 else "Decreased"} {stat.capitalize()} Chance')


def displayPassive(effect, noNewLine = False):
    if effect["buff"]:
        effectColor = "light green"
    else:
        effectColor = "light red"
    
    if type(effect["turns"]) is list:
        turnText = f'{effect["turns"][0]} - {effect["turns"][1]} turns'
    else:
        turnText = f'{effect["turns"]} turn{"s" if effect["turns"] > 1 else ""}'
    
    newLine = " " if noNewLine else "\n "
    print(f'{newLine}Applies {c(effectColor)}{effect["name"]}{reset} for {turnText}.')


def displayTags(tags, notes=False, extraSpace=False):
    begin = " "
    noteBegin = " - "
    if notes: begin, noteBegin = "  - ", "  - "
    if extraSpace: begin, noteBegin = "   - ", "   - "
    for tag in tags:
        name = tag.split(":")[0]
        try: value = tag.split(":")[1]
        except: value = False
        if name == "passive":
            print(f'{begin}', end="")
            displayPassive(newPassive(value), noNewLine=True)
        if name == "hit": print(f'{begin}Never misses.\n{begin}Undodgeable.')
        if name == "noMiss": print(f'{begin}Never misses.')
        if name == "noDodge": print(f'{begin}Undodgeable.')
        if name == "pierce":
            if value: print(f'{begin}Piercing: Ignores {value}% of enemy armor.')
            else: print(f'{begin}Piercing: Ignores enemy armor.')
        if name == "variance":
            if value == "0": print(f'{begin}Steadfast: Damage doesn\'t vary.')
            else: print(f'Random: {begin}Damage varies by {value}%.')
        if name == "infinite": print(f'{begin}Infinite: Item isn\'t lost on consumption.')
        if name == "lifesteal": print(f'{begin}Lifesteal: Heals for {value}% of damage dealt to an enemy.')


def displayItemStats(item):
    print("\n " + displayItem(item["name"], item["rarity"]))
    if item["type"] == "equipment": print(" Modifier:    " + displayItem(item["modifier"]["name"], item["modifier"]["rarity"]))
    print(" Rarity:      " + item["rarity"].capitalize())
    print(" Description: \"" + item["description"] + "\"")
    
    effects = {}
    p_passives = []
    if item["type"] not in ("item", "modifier"):
        for effect in item["effect"]:
            if effect["type"] == "passive":
                p_passives.append(effect["value"])
            if effect["type"] == "stat":
                effects.update({effect["stat"]: effect})
            else:
                if "passive" in effect:
                    for passive in effect["passive"]: p_passives.append(newPassive(passive))
                effects.update({effect["type"]: effect})
    if item["type"] == "equipment" and item["slot"] == "tome": print(f'\n Costs {c("blue")}{item["mana"]} ♦{reset}')
    
    displayEffect(effects)
    displayStats(effects)
    for effect in p_passives:
        displayPassive(effect, noNewLine=True)
    displayTags(item["tags"])
    
    if item["enchantments"] != []:
        print(c("light blue") + "\n Enchantments:" + reset)
        for enchantment in item["enchantments"]:
            print(f'  - {enchantment["name"]} {returnNumeral(enchantment["level"])}')


def displayQuest(quest, owned):
    print("\n " + displayItem(quest["name"], quest["rarity"]))
    print("\n Objectives:")
    for objective in quest["objective"]:
        if owned: print(f'  - {c("dark gray") if objective["complete"] else ""}{string.capwords(objective["type"])}{" " + str(objective["quantity"]) + "x" if objective["quantity"] > 1 else ""} {objective["name"]} ({objective["status"]}/{objective["quantity"]}){reset}')
        else: print(f'  - {string.capwords(objective["type"])}{" " + str(objective["quantity"]) + "x" if objective["quantity"] > 1 else ""} {objective["name"]}')


def displayPlayerTitle():
    print(f' {player.name} [Lvl {player.level}]')


def displayPlayerGold():
    print(f' Gold: {c("yellow")}● {reset}{player.gold}')


def displayPassives(entity):
    if len(entity.passives) > 0:
        print(" ", end="")
        print(", ".join([f'{c("light green" if passive["buff"] else "light red")}{passive["name"]}{reset} ({passive["turns"]})' for passive in entity.passives]))


def displayPlayerStats(passives=True):
    print("")
    displayPlayerTitle()
    print("", returnHpBar(player))
    print("", returnMpBar(player))
    print(returnXpBar(player))
    displayPlayerGold()
    if passives: displayPassives(player)


def displayBattleStats(player, enemy, playerDamage = 0, enemyDamage = 0):
        if playerDamage > 0: playerDamageText = " +" + str(playerDamage)
        elif playerDamage < 0: playerDamageText = " " + str(playerDamage)
        else: playerDamageText = ""
        if enemyDamage > 0: enemyDamageText = " +" + str(enemyDamage)
        elif enemyDamage < 0: enemyDamageText = " " + str(enemyDamage)
        else: enemyDamageText = ""
        
        cols = os.get_terminal_size()[0]
        rows = os.get_terminal_size()[1]
        barWidth = int(cols // 3.4)
        if barWidth % 2 == 0: barWidth -= 1
        leftPad, midPad = 0, 0
        barPadding = int((cols - barWidth * 2) / 3)
        if cols % 3 == 0: leftPad, midPad = barPadding, barPadding
        elif cols % 2 == 0: leftPad, midPad = barPadding + 1, barPadding
        else: leftPad, midPad = barPadding, barPadding + 1
        
        
        playerTitle = f'- {player.name} -'
        enemyTitle = f'- {enemy.name} [Lvl {enemy.level}] -'
        if len(playerTitle) <= barWidth and len(enemyTitle) <= barWidth:
            print("\n", " "*leftPad, playerTitle.center(barWidth), " "*midPad, enemyTitle.center(barWidth), sep="")
        else:
            print("\n", "  ", player.name, " vs ", enemy.name, sep="")
        print(c("red"))
        if rows >= 42: print(" "*leftPad, "♥".center(barWidth), " "*midPad, "♥".center(barWidth), sep="")
        print(" "*leftPad, returnHpBar(player, text=False, length=barWidth), " ", playerDamageText.ljust(midPad), returnHpBar(enemy, text=False, length=barWidth), " ", enemyDamageText, sep="")
        print(" "*leftPad, str(player.hp).rjust(barWidth // 2 - 1), " / ", str(player.stats["max hp"]).ljust(barWidth // 2 - 1), " "*midPad, str(enemy.hp).rjust(barWidth // 2 - 1), " / ", str(enemy.stats["max hp"]).ljust(barWidth // 2 - 1), sep="")
        print(c("blue"))
        if rows >= 42: print(" "*leftPad, "♦".center(barWidth), " "*midPad, "♦".center(barWidth), sep="")
        print(" "*leftPad, returnMpBar(player, text=False, length=barWidth), " "*midPad, returnMpBar(enemy, text=False, length=barWidth), sep="")
        print(" "*leftPad, str(player.mp).rjust(barWidth // 2 - 1), " / ", str(player.stats["max mp"]).ljust(barWidth // 2 - 1), " "*midPad, str(enemy.mp).rjust(barWidth // 2 - 1), " / ", str(enemy.stats["max mp"]).ljust(barWidth // 2 - 1), sep="")
        displayPassives(player)
        displayPassives(enemy)
        print("")


def printError():
    errType, errValue, errTraceback = sys.exc_info()
    trace_back = traceback.extract_tb(errTraceback)
    stackTrace = list()
    for trace in trace_back:
        stackTrace.append(f'{trace[2]} [{trace[1]}]: {trace[3]}')
    print("\n Exception at " + time.ctime(time.time()))
    print(" " + str(errType.__name__) + ": " + str(errValue))
    print(" " + str(stackTrace[-1]))
    print(" " + str(stackTrace[:-2]))


# Text returning

def drawBar(max, value, color, length):
    text = "".center(length, "■")
    if round(value/max*length) > 0: text = c(color) + c("dark " + color, True) + text[:round((value/max)*length)] + c("gray") + c("dark gray", True) + text[round((value/max)*length):] + reset
    else: text = c("gray") + c("dark gray", True) + text + reset
    return text


def returnHpBar(entity, text=True, length=32):
    bar = f'{c("red")}{"♥ " if text else ""}{drawBar(entity.stats["max hp"], entity.hp, "red", length)}'
    if text: bar += f' {entity.hp}/{entity.stats["max hp"]}'
    return bar


def returnMpBar(entity, text=True, length=32):
    bar = f'{c("blue")}{"♦ " if text else ""}{drawBar(entity.stats["max mp"], entity.mp, "blue", length)}'
    if text: bar += f' {entity.mp}/{entity.stats["max mp"]}'
    return bar


def returnXpBar(entity, text=True, length=32):
    bar = f' {c("green")}• {drawBar(entity.mxp, entity.xp, "green", length)}'
    if text: bar += f' {entity.xp}/{entity.mxp}'
    return bar


def returnNumeral(number):
    if number <= 3: return "I"*number
    elif number == 4: return "IV"
    elif number == 5: return "V"
    elif number <= 8: return "V" + "I"*(number-5)
    elif number == 9: return "IX"
    elif number == 10: return "X"
    else: return str(number)





#  .::::::.   .,-:::::  :::::::..   .,::::::  .,::::::  :::.    :::. .::::::. 
# ;;;`    ` ,;;;'````'  ;;;;``;;;;  ;;;;''''  ;;;;''''  `;;;;,  `;;;;;;`    ` 
# '[==/[[[[,[[[          [[[,/[[['   [[cccc    [[cccc     [[[[[. '[['[==/[[[[,
#   '''    $$$$          $$$$$$c     $$""""    $$""""     $$$ "Y$c$$  '''    $
#  88b    dP`88bo,__,o,  888b "88bo, 888oo,__  888oo,__   888    Y88 88b    dP
#   "YMmMY"   "YUMMMMMP" MMMM   "W"  """"YUMMM """"YUMMM  MMM     YM  "YMmMY" 


# Main Menu

def s_mainMenu():
    i = 0
    while 1:
        i += 1
        clear()
        if i == 1: write("\n Welcome to the world of...", speed=0.01)
        else: print("\n Welcome to the world of...\n")

        if os.get_terminal_size()[0] >= 103:
            title = openTextAsList("data/text/magyka title.txt", splitter="\n")
            for i in range(len(title)):
                print(cc(["026", "012", "006", "039", "045", "019", "020", "021", "004", "027", "026", "012", "006", "039", "000", "039", "006", "012"][i]) + title[i] + reset)
        else:
            title = openTextAsList("data/text/magyka title small.txt", splitter="\n")
            for i in range(len(title)):
                print(cc(["026", "026", "006", "045", "018", "004", "026", "006", "000", "039"][i]) + title[i] + reset)

        options(["New Game", "Continue", "Quit"])
        option = command(back = False, options = "ncq")

        if option == "n": s_newGame()
        elif option == "c": s_continue()
        elif option == "q": exitGame()
        if returnTo(): break


def s_newGame():
    clear()

    text = openTextAsList("data//text/new game.txt")
    write(evalText(text[0]), textSpeed)

    while 1:
        option = command(True, "alphanumeric", back = False)

        if option == "" or option == None: print(c("light red") + "\n Your name cannot be empty." + reset)
        elif option == "D":
            clear()
            write(evalText(text[0]), 0)
            continue
        elif len(option) <= 2: print(c("light red") + "\n Your name cannot be less than 2 characters long." + reset)
        elif len(option) >= 15: print(c("light red") + "\n Your name cannot be greater than 15 characters long." + reset)
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
    page = 1
    while 1:
        clear()

        print("\n -= Load =-")
        print("\n Which file are you loading?")

        if len(saves) > 0: print("")
        else: print("\n " + c("dark gray") + "- Empty -" + reset)

        for i in range(-10 + 10*page, 10*page if 10*page < len(saves) else len(saves)):
            print(f' {i}) {saves[i][1]} | {saves[i][0].name} [Lvl {saves[i][0].level}]')

        option = command(False, "optionumeric", options = "".join(tuple(map(str, range(0, len(saves))))))

        if option in tuple(map(str, range(0, len(saves)+ (page-1) * 10 + 1))):
            player = saves[int(option) + (page-1) * 10][0]
            s_camp()
        elif option in ("B"): break
        if returnTo(): break


# Camp

def s_camp():
    while 1:
        if returnTo(): break
        clear()

        print("\n -= Camp =-")
        displayPlayerStats()
        print(openEvalText("data//text//screens//camp.txt"))
        
        options(["Explore", "Town", "Character", "Save", "Quit"])
        option = command(back = False, options = "etcosq")

        if option == "e": s_explore()
        elif option == "t": s_town()
        elif option == "c": s_character()
        elif option == "s": s_save()
        elif option == "q": s_quit()


# Explore

def s_explore():
    page = 1
    while 1:
        clear()

        print("\n -= Explore =-")
        displayPlayerStats()
        print(openEvalText(f'data//text//screens//{player.location} explore.txt'))
        print("\n Discovered Locations:\n")
        locations = player.locations[player.location]
        
        for i in range(-10 + 10*page, 10*page if 10*page < len(locations) else len(locations)):
            print(f' {str(i)[:-1]}({str(i)[-1]}) {string.capwords(locations[i])}')

        if len(locations) == 0:
            print(" " + c("dark gray") + "- No Locations Discovered -" + reset)

        next = len(locations) > page*10 + 1
        previous = page != 1

        options(["Search", c("dark gray") + "Map"] + (["Next"] if next else []) + (["Previous"] if previous else []))
        option = command(False, "optionumeric", options="sm" + ("n" if next else "") + ("p" if previous else "") + "".join(tuple(map(str, range(0, len(locations))))))

        if option in tuple(map(str, range(0, len(locations) + (page-1) * 10 + 1))) + tuple(["s"]):
            areaEnemies = loadEncounter(player.location, "hunt" if option == "s" else locations[int(option) + (page-1) * 10])
                
            weight = 0
            level = random.randint(1, 3)
            if level == 1: level = player.level - 1 if player.level > 1 else 1
            elif level == 2: level = player.level
            else: level = player.level + 1

            for i in range(len(areaEnemies)-1, -1, -1):
                if areaEnemies[i][1].level[0] > level or areaEnemies[i][1].level[1] < level:
                    areaEnemies.pop(i)
                    continue

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

            areaEnemies = dict(areaEnemies[::-1])
            try:
                enemyNum = random.randint(1, weight)
            except:
                print("\n You don't spot any monsters. You're too low of a level.")
                pressEnter()
                continue
            for enemy in areaEnemies:
                if enemyNum <= enemy:
                    enemy = areaEnemies[enemy]
                    break
            
            print(f'\n You spot {enemy.name} [Lvl {enemy.level}]. Do you fight?')

            options(["Yes", "No"])
            while 1:
                option = command(back = False, options = "yn")

                if option == "y":
                    s_battle(enemy)
                    break
                elif option == "n":
                    print(f'\n You quiety slip away from {enemy.name} [Lvl {enemy.level}].')
                    pressEnter()
                    break
        elif option == "m": pass
        elif option == "B": break
        if returnTo(): break


def s_battle(enemy):
    itemLog = []
    if type(enemy.level) is list: enemy.level = enemy.level[0]
    
    def attack(target, effectList, offense, defense, tags = False):
        if tags == None: tags = []
        effectList = copy.deepcopy(effectList)
        for effect in effectList:
            if "passive" in effect:
                for i in range(len(effect["passive"])):
                    effect["passive"][i] = newPassive(effect["passive"][i])
                passive = effect["passive"]
            else: passive = False
            
            defenseDamage = 0
            offenseDamage = 0
            
            if target == "self": text, defenseDamage = offense.defend(effect, offense.stats, (tags if not tags == False else effect["tags"]), passive)
            else:
                text, offenseDamage = defense.defend(effect, offense.stats, (tags if not tags == False else effect["tags"]), passive)
                for tag in (tags if not tags == False else effect["tags"]):
                    if tag.split(":")[0] == "lifesteal":
                        heal = math.ceil(abs(offenseDamage)/int(tag.split(":")[1]))
                        if heal > 0:
                            text += f' {offense.name} lifesteals {c("red")}{heal} ♥{reset}.'
                            offense.defend({"type": "hp", "value": heal})
                            defenseDamage += heal            
            return text, defenseDamage, offenseDamage

    while 1:
        player.guard = ""
        text = [""]
        playerDamage, enemyDamage = 0, 0
        over = False
        while 1:
            clear()
            displayBattleStats(player, enemy)
            
            usedItem = False
            canUseMagic = False if player.equipment["tome"] == "" or player.mp < player.equipment["tome"]["mana"] else True

            options(["Attack", (c("dark gray") if not canUseMagic else "") + "Magic", "Guard", "Item", "Flee"], True)
            option = command(back = False, options = "amgif" if canUseMagic else "agif", horizontal=True, silent=True)

            if enemy.guard == "counter":
                text[0], playerDamage = player.defend(enemy.attack(), enemy.stats)
                text[0] = f' {player.name} attacks {enemy.name}, ' + evalText(text[0])
                break
            if option == "a":
                tempText, defenseDamage, offenseDamage = attack("enemy", [player.attack()], player, enemy, player.equipment["weapon"]["tags"])
                text[0] = f' {player.name} attacks {enemy.name}, ' + evalText(text[0])
                text[0] += tempText
                playerDamage += defenseDamage
                enemyDamage += offenseDamage
                break
            elif option == "m":
                tempText, defenseDamage, offenseDamage = attack(player.equipment["tome"]["target"], player.get_magic(), player, enemy, player.equipment["tome"]["tags"])
                text[0] = f' {player.name} casts {player.equipment["tome"]["text"]} on {player.name if player.equipment["tome"]["target"] == "self" else enemy.name}, '
                text[0] += tempText
                playerDamage += defenseDamage
                enemyDamage += offenseDamage
                player.mp -= player.equipment["tome"]["mana"]
                break
            elif option == "g":
                guardState = random.randint(1, 5)
                if guardState <= 3: player.guard = "deflect"
                elif guardState == 4: player.guard = "block"
                else: player.guard = "counter"
                text[0] = f' {player.name} lowers into a defensive stance.'
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

                    if option in tuple(map(str, range(0, len(itemList) + (page-1) * 10 + 1))):
                        item = itemList[int(option) + (page-1) * 10][0]
                        while 1:
                            clear()
                            player.updateStats()

                            print(f'\n -= Inspect Consumable =-')

                            displayItemStats(item)
                            print(f'\n Value: {c("yellow")}● {reset}{item["value"]}')

                            options(["Use"])
                            option1 = command(False, "alphabetic", options = "u")

                            usedItem = False
                            if option1 == "u":
                                usedItem = True
                                tempText, defenseDamage, offenseDamage = attack(item["target"], item["effect"], player, enemy, item["tags"])
                                text[0] = f' {player.name} {item["text"]} {displayItem(item["name"], item["rarity"], 1)}{"" if item["target"] == "self" else " on " + enemy.name}, '
                                text[0] += tempText
                                playerDamage += defenseDamage
                                enemyDamage += offenseDamage

                                if "infinite" not in item["tags"]: player.removeItem(item)

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
                        if random.randint(1, 2) == 1:
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

        if enemy.hp <= 0 or player.hp <= 0: over = True
        tempText, tempDamage = player.update()
        text += tempText
        playerDamage += tempDamage
        clear()
        displayBattleStats(player, enemy, playerDamage=playerDamage, enemyDamage=enemyDamage)
        for line in text:
            printLine = evalText(line).center(os.get_terminal_size()[0] + evalText(line).count("\x1b[3") * 9 + line.count("{reset}") * 3)
            print("\n", printLine, sep="")
        if enemy.hp <= 0 or player.hp <= 0 or over: break
        pressEnter(horizontal=True)

        # LOGIC FOR ENEMY ATTACK
        enemy.guard = ""
        text = [""]
        playerDamage, enemyDamage = 0, 0
        attackType = random.randint(1,5)
        if attackType <= 2: attackType = "attack"
        elif attackType <= 4: attackType = "magic"
        else: attackType = "guard"

        if player.guard == "counter":
            text[0], enemyDamage = enemy.defend(player.attack(), player.stats)
            text[0] = f' {player.name} counters {enemy.name}, ' + evalText(text[0])
            attackType = ""
        if attackType == "magic":
            if enemy.magic != None:
                castable = []
                for effect in enemy.magic:
                    if enemy.magic["mana"] <= enemy.mp: castable.append(effect)
                if len(castable) == 0: attackType = "attack"
                else:
                    magic = castable[random.randint(1, len(castable))]
                    tempText, defenseDamage, offenseDamage = attack(magic["target"], magic["effect"], enemy, player)
                    text[0] = f' {enemy.name} casts {magic["text"]} on {player.name}, '
                    text[0] += tempText
                    enemyDamage += defenseDamage
                    playerDamage += offenseDamage
                    enemy.mp -= magic["mana"]
            else: attackType = "attack"
        if attackType == "guard":
            if enemy.hp <= enemy.stats["max hp"] // 2:
                guardState = random.randint(1, 5)
                if guardState <= 3: enemy.guard = "deflect"
                elif guardState == 4: enemy.guard = "block"
                else: enemy.guard = "counter"
                print(f' {enemy.name} lowers into a defensive stance.')
            else: attackType = "attack"
        if attackType == "attack":
            tempText, defenseDamage, offenseDamage = attack("enemy", [enemy.attack()], enemy, player, enemy.tags)
            text[0] = f' {enemy.name} {enemy.text} {player.name}, ' + evalText(text[0])
            text[0] += tempText
            enemyDamage += defenseDamage
            playerDamage += offenseDamage

        if enemy.hp <= 0 or player.hp <= 0: over = True
        tempText, tempDamage = enemy.update()
        text += tempText
        enemyDamage += tempDamage
        clear()
        displayBattleStats(player, enemy, playerDamage=playerDamage, enemyDamage=enemyDamage)
        for line in text:
            printLine = evalText(line).center(os.get_terminal_size()[0] + evalText(line).count("\x1b[3") * 9 + line.count("{reset}") * 3)
            print("\n", printLine, sep="")
        if enemy.hp <= 0 or player.hp <= 0 or over: break
        pressEnter(horizontal=True)
    pressEnter(horizontal=True)
    
    if enemy.hp <= 0: s_victory(enemy, itemLog)
    else: s_defeat(enemy, itemLog)


def s_victory(enemy, itemLog):
    clear()
    print("\n -= Victory =-")
    player.updateQuests(enemy=enemy)

    levelDifference = enemy.level - player.level
    if levelDifference == 0: lootMultiplier = 1
    else: lootMultiplier = max(round(1.25 ** levelDifference, 2), 0.6)
    xp = math.ceil(enemy.xp * lootMultiplier)
    gold = math.ceil(random.randint(math.ceil(enemy.gold*0.9), math.ceil(enemy.gold*1.1)) * lootMultiplier)
    items = []
    if enemy.items != None:
        for item in enemy.items:
            if random.randint(1, 100) <= item[2]:
                if type(item[1]) is list: items.append([newItem(item[0]), random.randint(item[1][0], item[1][1])])
                else: items.append([newItem(item[0]), item[1]])

    for item in items:
        player.addItem(item[0], item[1])
    player.gold += gold
    player.xp += xp
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
    if player.completedQuests != []:
        print("\n ! COMPLETED QUEST !")
        for quest in player.completedQuests:
            print(f'  - Completed {displayItem(quest["name"], quest["rarity"])}')
        player.completedQuests = []
    
    pressEnter()
    if player.levelsGained > 0: s_levelUp()


def s_defeat(enemy, itemLog):
    clear()

    print("\n -= Defeat =-")
    print("\n Defeated by:")
    print(f'\n {enemy.name} [Lvl {enemy.level}]')
    print(f' {c("red")}♥ {drawBar(enemy.stats["max hp"], enemy.hp, "red", 32)} {enemy.hp}/{enemy.stats["max hp"]}')
    print(f' {c("blue")}♦ {drawBar(enemy.stats["max mp"], enemy.mp, "blue", 32)} {enemy.mp}/{enemy.stats["max mp"]}')
    
    if len(enemy.passives) > 0:
        print(" ", end="")
        print(", ".join([f'{c("light green" if passive["buff"] else "light red")}{passive["name"]}{reset} ({passive["turns"]})' for passive in enemy.passives]))
    print("\n Items used: " + (c("gray") + "- None -" + reset if len(itemLog) < 1 else ""))

    for item in itemLog:
        print(f' - {displayItem(item[0]["name"], item[0]["rarity"], item[1])}')

    itemLog = []
    player.addPassive(newPassive("Charon's Curse"))
    player.hp = player.stats["max hp"]
    player.mp = player.stats["max mp"]//3
    pressEnter()


def s_levelUp():
    while 1:
        clear()
        print(f'\n -= Level Up =-')
        print(f'\n {player.name} leveled up to level {player.level - player.levelsGained + 1}!')
        print("\n Choose an attribute to spend a point in, or pick a random attribute.")
        
        options(["Health", "Mana", "Vitality", "Dodge Chance", "Crit Chance", "Random"])
        option = command(False, "alphabetic", options = "hsvdcr", back = False)
        
        if option == "r":
            option = "hmvdc"[random.randint(0, 6)]
        
        if option == "h":
            player.baseStats["max hp"] = math.ceil(player.baseStats["max hp"] * 1.05)
            player.updateStats()
            player.hp = player.stats["max hp"]
        elif option == "m":
            player.baseStats["max mp"] = math.ceil(player.baseStats["max mp"] * 1.05)
            player.updateStats()
            player.mp = player.stats["max mp"]
        elif option == "s":
            player.baseStats["strength"] += 1
            player.updateStats()
        elif option == "i":
            player.baseStats["intelligence"] += 1
            player.updateStats()
        elif option == "v":
            player.baseStats["vitality"] += 1
            player.updateStats
        elif option == "d":
            player.baseStats["dodge"] += 3
            player.updateStats()
        elif option == "c":
            player.baseStats["crit"] += 4
            player.updateStats()
        else: continue
        
        player.levelsGained -= 1
        
        if player.levelsGained <= 0:
            return


# Town

def s_town():
    while 1:
        clear()

        print("\n -= Town of Fordsville =-")
        displayPlayerStats()
        print(openEvalText(f'data//text//screens//{player.location} town.txt'))

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

        options(["Rest", "Quest", c("dark gray") + "Gamble"])
        option = command(False, "alphabetic", options = "rq")

        if option == "r":
            if player.gold >= price:
                player.gold -= price
                player.hp = player.stats["max hp"]
                player.mp = player.stats["max mp"]
                player.addPassive(newPassive("Well Rested"))
                player.updateStats()
                print(f'\n You feel well rested. HP and MP restored to full!')
                pressEnter()
            else:
                print(f'\n {c("yellow")}Barkeep:{reset} You don\'t have enough coin to stay.')
                pressEnter()
        elif option == "q": pass
        elif option == "g": pass
        elif option == "B": break
        if returnTo(): break


def s_quest():
    while 1:
        clear()
        print("\n -= Quest =-")
        
        quest = None
        questInProgress = False
        
        for q in quests[player.location]:
            if q["name"] not in player.completedMainQuests[player.location]:
                quest = copy.deepcopy(q)
                quest.update({"main": True})
                if quest.get("location") == None: quest.update({"location": [player.location]})
                break
        
        for q in player.quests:
            if q["name"] == quest["name"]:
                questInProgress = True
                break
        
        if not quest:
            pass#random quest generation here (happens after main quests are finished)
        
        if quest != None:
            displayQuest(quest, False)
            if questInProgress: print("\n Quest in progress.")
            else: print("\n Do you accept the quest, adventurer?")
        else:
            questInProgress = True
            print("\n No quests at this time. Come back later!")
        
        options([] if questInProgress else ["Yes", "No"])
        option = command(False, "alphabetic", options=("" if questInProgress else "yn"))
        
        if option == "y":
            player.addQuest(quest)
            print("\n Quest added: " + displayItem(quest["name"], quest["rarity"]))
            pressEnter()
            break
        elif option in ("n", "B"): break
        if returnTo(): break


def s_store(store):
    page = 1
    while 1:
        clear()
        storeData = loadStore(player.location, store)
        itemList = []
        
        for item in storeData["inventory"]:
            if item in items:
                itemList.append(newItem(item))
            else:
                print(f' "{item}" does not exist.')
        next = False if len(itemList) < (page+1)*10 else True
        previous = False if page == 1 else True

        print(f'\n -= {store.capitalize()} =-')
        print(evalText(storeData["description"]))
        print("\n Equipment:\n")
        for i in range(len(slotList)):
            if player.equipment[slotList[i]] != "": print(f'  - {displayItem(player.equipment[slotList[i]]["name"], player.equipment[slotList[i]]["rarity"])}')
        print("")
        displayPlayerGold()
        print("")

        for i in range(-10 + 10*page, 10*page if 10*page < len(itemList) else len(itemList)):
            print(f' {i}) {displayItem(itemList[i]["name"], itemList[i]["rarity"], 1 if itemList[i]["type"] in stackableItems else 0)} {c("yellow")}●{reset} {itemList[i]["value"]}')
            

        if len(itemList) == 0: print(" " + c("dark gray") + "- Empty -" + reset)

        options((["Next"] if next else []) + (["Previous"] if previous else []) + (["Reforge"] if store == "blacksmith" else []))
        option = command(False, "optionumeric", options = ("n" if next else "") + ("p" if previous else "") + ("r" if store == "blacksmith" else "") + "".join(tuple(map(str, range(0, len(itemList))))))

        if option in tuple(map(str, range(0, len(itemList) + (page-1) * 10 + 1))): s_purchase(itemList[int(option) + (page-1) * 10])
        elif option == "r": s_reforge()
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
        print(f'\n Currently owned: {player.numOfItems(item["name"])}')

        print(f'\n Type the quantity of items to be purchased ({player.gold // item["value"]} can be bought).')

        option = command(True, "numeric")

        if option == "B": break
        elif option == "D": pass
        elif int(option) <= player.gold // item["value"] and int(option) > 0:
            player.addItem(item, int(option))
            player.gold -= item["value"] * int(option)
            print(f'\n {displayItem(item["name"], item["rarity"], int(option))} added to your inventory.')
            pressEnter()
            break
        else:
            print(f'\n {c("light red")}You don\'t have enough gold to buy {item["name"]} x{int(option)}.')
            pressEnter()
        if returnTo(): break


def s_reforge():
    while 1:
        clear()
        print("\n -= Reforge =-")
        print("\n Type the number of the item you wish to reforge.\n")

        for i in range(len(slotList)):
            item = player.equipment[slotList[i]]
            if item == "":
                print(f' {i}) {c("dark gray")} - Empty -{reset}')
                continue
            item = updateEquipment(item)
            print(f' {i}) {displayItem(item["name"], item["rarity"])}: {displayItem(item["modifier"]["name"], item["modifier"]["rarity"])} {c("yellow")}●{reset} {item["value"] // 2}')

        option = command(False, "numeric", options = "".join(tuple(map(str, range(0, len(slotList))))))

        if option in tuple(map(str, range(0, len(slotList)))) and player.equipment[slotList[int(option)]] != "":
            slot = slotList[int(option)]
            price = player.equipment[slot]["value"] // 2
            item = player.equipment[slot]
            if player.gold >= price:
                if slot in ("helmet", "chest", "legs", "feet"): slot = "armor"
                modifier = random.randint(0, len(modifiers[slot])-1)
                modifier = modifiers[slot][modifier]
                player.equipment[slotList[int(option)]] = modifyEquipment(player.equipment[slotList[int(option)]], newModifier(modifier))
                print(f'\n Successfuly reforged {displayItem(item["name"], item["rarity"])} to {displayItem(item["modifier"]["name"], item["modifier"]["rarity"])}.')
                pressEnter()
            else:
                print(f'\n You don\'t have enough gold.')
                pressEnter()
        elif option == "B": break


def s_enchant():
    while 1:
        clear()
        print("\n -= Enchant =-")
        print("\n Type the number of the item you wish to enchant.")
        print("\n You cannot enchant an item that is already enchanted.\n")
        
        for i in range(len(slotList)):
            item = player.equipment[slotList[i]]
            if item == "":
                print(f' {i}) {c("dark gray")} - Empty -{reset}')
                continue
            item = updateEquipment(item)
            enchanted = player.equipment[slotList[i]]["enchantments"] != []
            if enchanted: print(f' {i}) {c("dark gray")}{item["name"]}{reset}')
            else: print(f' {i}) {displayItem(item["name"], item["rarity"])} {c("yellow")}●{reset} {item["value"] // 2 + 15 + round(player.level ** 1.5)}')
        
        option = command(False, "numeric", options = "".join(tuple(map(str, range(0, len(slotList))))))
        
        if option in tuple(map(str, range(0, len(slotList)))) and player.equipment[slotList[int(option)]] != "" and player.equipment[slotList[int(option)]]["enchantments"] == []:
            slot = slotList[int(option)]
            item = player.equipment[slot]
            price = item["value"] // 2 + 15 + round(player.level ** 1.5)
            if player.gold >= price:
                if slot in ("helmet", "chest", "legs", "feet"): slot = "armor"
                numEnchantments = random.randint(1,100)
                currentEnchantments = []
                if numEnchantments <= 30: numEnchantments = 1
                elif numEnchantments <= 70: numEnchantments = 2
                elif numEnchantments <= 85: numEnchantments = 3
                elif numEnchantments <= 95: numEnchantments = 4
                elif numEnchantments <= 99: numEnchantments = 5
                else: numEnchantments = 6
                
                while len(currentEnchantments) < numEnchantments:
                    enchantment = random.randint(0, len(enchantments[slot])-1)
                    i = 0
                    for enchant in enchantments[slot]:
                        if i == enchantment:
                            enchantment = enchant
                            break
                        i += 1
                    if enchantment not in currentEnchantments: currentEnchantments.append(enchantment)
                
                for enchantment in currentEnchantments:
                    e = enchantments[slot][enchantment]
                
                    if player.level <= 20: tier = 0
                    elif player.level <= 40: tier = 1
                    else: tier = 2
                    
                    if e == 1: level = 1
                    elif e == 2: level = random.randint(1, 2)
                    else:
                        if player.level >= 61: level = random.randint(e - 1, e)
                        elif player.level % 20 <= 10: level = random.randint(1, e // 2)
                        else: level = random.randint(e // 2, e)
                    if level < 1: level = 1
                    
                    player.equipment[slotList[int(option)]] = enchantEquipment(player.equipment[slotList[int(option)]], newEnchantment(enchantment, tier, level))
                    player.updateStats()
                player.gold -= price
                print(f'\n Successfuly enchanted {displayItem(item["name"], item["rarity"])}.')
                pressEnter()
            else:
                print(f'\n You don\'t have enough gold.')
                pressEnter()
        elif option == "B": break


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

        if option in tuple(map(str, range(0, len(player.inventory) + (page-1) * 10 + 1))):
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
        elif option != "D":
            print("\n You cannot sell that many.")
            pressEnter()
        if returnTo(): return


# Character

def s_character():
    while 1:
        clear()

        print("\n -= Character =-")
        displayPlayerStats()

        options(["Inventory", "Equipment", "Crafting", "Quests", "Stats"])
        option = command(options = "iecqs")

        if option == "i": s_inventory()
        elif option == "e": s_equipment()
        elif option == "c": s_crafting()
        elif option == "q": s_quests()
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

        if option in tuple(map(str, range(0, len(player.inventory) + (page-1) * 10 + 1))):
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
        if equipped:
            player.equipment[item["slot"]] = updateEquipment(player.equipment[item["slot"]])
            item = player.equipment[item["slot"]]
        player.updateStats()

        print(f'\n -= Inspect {item["type"].capitalize()} =-')
        displayItemStats(item)
        print(f'\n Value: {c("yellow")}● {reset}{item["value"]}')

        if item["type"] == "equipment":
            options((["Unequip"] if equipped else ["Equip", "Discard"])+["More Info"])
            option = command(False, "alphabetic", options=("u" if equipped else "ed")+"m")
        elif item["type"] == "consumable":
            options((["Use"] if item["target"] == "self" else [])+["Discard"])
            option = command(False, "alphabetic", options=("u" if item["target"] == "self" else "")+"d")
        elif item["type"] == "modifier":
            options(["Use", "Discard"])
            option = command(False, "alphabetic", options="ud")
        else:
            options(["Discard"])
            option = command(False, "alphabetic", options="d")

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
            text[0] = f'\n {player.name} {item["text"]} {displayItem(item["name"], item["rarity"], 1)}, ' + text[0]
            for line in text:
                print(evalText(line))
            pressEnter()
            if "infinite" not in item["tags"]: player.removeItem(item)
            if player.numOfItems(item["name"]) <= 0: break
        elif item["type"] == "modifier" and option == "u":
            s_applyModifier(item)
            if "infinite" not in item["tags"]: player.removeItem(item)
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
        elif option == "m": s_inspectDetailed(item["modifier"], item["enchantments"])
        elif option == "B": break
        if returnTo(): break


def s_inspectDetailed(modifier, enchantments):
    while 1:
        clear()
        print("\n -= More Info =-")
        
        print("\n " + displayItem(modifier["name"], modifier["rarity"]) + ":")
        effects = {}
        for effect in modifier["effect"]:
            effects.update({effect["type"]: effect})
        displayEffect(effects, notes=True)
        displayTags(modifier["tags"], notes=True)
        if modifier["name"] == "Normal": print("  - No effect.")
        
        if enchantments != []:
            print(c("light blue") + "\n Enchantments:" + reset)
            for enchantment in enchantments:
                print(f'  {enchantment["name"]} {returnNumeral(enchantment["level"])}:')
                effects = {}
                for effect in enchantment["effect"]:
                    effects.update({effect["type"]: effect})
                displayEffect(effects, notes=True, extraSpace=True)
                displayTags(enchantment["tags"], notes=True, extraSpace=True)
        
        pressEnter()
        break


def s_applyModifier(modifier):
    page = 1
    while 1:
        clear()

        print("\n -= Apply Modifier =-\n")
        
        itemList = []
        equipped = False
        if player.equipment[modifier["slot"]] != "":
            equipped = True
            itemList += [[player.equipment[modifier["slot"]], 1]]
        itemList += [item for item in player.inventory if "slot" in item[0] and item[0]["slot"] == modifier["slot"] and item[0]["type"] == "equipment"]

        for i in range(-10 + 10*page, 10*page if 10*page < len(itemList) else len(itemList)):
            equipText = ""
            if equipped and i == 0: equipText = " ( EQUIPPED )"
            print(f' {str(i)[:-1]}({str(i)[-1]}) {displayItem(itemList[i][0]["name"], itemList[i][0]["rarity"], (itemList[i][1] if itemList[i][0]["type"] in stackableItems else 0))}{equipText}')

        if len(itemList) == 0:
            print(" " + c("dark gray") + "- Nothing Applicable -" + reset)

        next = len(itemList) > page*10 + 1
        previous = page != 1

        options((["Next"] if next else []) + (["Previous"] if previous else []))
        option = command(False, "optionumeric", options = ("n" if next else "") + ("p" if previous else "") + "".join(tuple(map(str, range(0, len(itemList))))))

        if option in tuple(map(str, range(0, len(itemList) + (page-1) * 10 + 1))):
            item = itemList[int(option) + (page-1) * 10][0]
            for enchantment in modifier["enchantments"]:
                item = enchantEquipment(item, enchantment)
            print(f'\n Successfully applied {displayItem(modifier["name"], modifier["rarity"])} to {displayItem(item["name"], item["rarity"])}.')
            pressEnter()
            break
        elif option == "n" and next: page += 1
        elif option == "p" and previous: page -= 1
        elif option == "B": break
        if returnTo(): return


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

        if option in tuple(map(str, range(0, len(unlockedRecipes) + (page-1) * 10 + 1))):
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
        print(f'\n Value: {c("yellow")}● {reset}{item["value"]}')
        
        craftable = True
        numCraftable = 999999999
        print(f'\n Requires:\n')
        for i in range(len(recipe["ingredients"])):
            playerIngredientCount = player.numOfItems(recipe["ingredients"][i][0])
            recipeIngredientRequirement = recipe["ingredients"][i][1]
            if playerIngredientCount < recipeIngredientRequirement:
                craftable = False
                numCraftable = 0
            elif playerIngredientCount // recipeIngredientRequirement < numCraftable:
                numCraftable = playerIngredientCount // recipeIngredientRequirement
            print(f' {recipeIngredientRequirement}x {displayItem(recipe["ingredients"][i][0], items[recipe["ingredients"][i][0]]["rarity"], 0)} ({playerIngredientCount}/{recipeIngredientRequirement})')
        
        if item["type"] == "equipment" and craftable: numCraftable = 1
        print(f'\n Type the quantity of items to be crafted ({numCraftable} craftable).')
        option = command(True, "numeric")
        
        if option == "B": break
        elif option == "D": continue
        elif int(option) <= numCraftable:
            for i in recipe["ingredients"]:
                player.removeItem(newItem(i[0]), i[1] * int(option))
            player.addItem(item, recipe["quantity"] * int(option))
            print(f'\n Crafted {displayItem(item["name"], item["rarity"], (int(option) * recipe["quantity"] if item["type"] in stackableItems else 0))}!')
            pressEnter()
            break
        else:
            print("\n You cannot craft that many.")
            pressEnter()
        if returnTo(): return


def s_quests():
    page = 1
    while 1:
        clear()
        print("\n -= Quests =-\n")
        
        quests = copy.deepcopy(player.quests)
        mainQuest = None
        for quest in quests:
            if quest.get("main") != None:
                mainQuest = quest
                quests.remove(quest)
                break
        
        for i in range(-10 + 10*page, 10*page if 10*page < len(quests) else len(quests)):
            print(f' {str(i)[:-1]}({str(i)[-1]}) {displayItem(quests[i]["name"], quests[i]["rarity"], 0)}')

        if len(quests) == 0:
            print(" " + c("dark gray") + "- No Side Quests -" + reset)

        next = len(quests) > page*10 + 1
        previous = page != 1

        options((["Next"] if next else []) + (["Previous"] if previous else []) + (["Main Quest"] if mainQuest != None else []))
        option = command(False, "optionumeric", options = ("n" if next else "") + ("p" if previous else "") + ("m" if mainQuest != None else "") + "".join(tuple(map(str, range(0, len(quests))))))

        if option in tuple(map(str, range(0, len(quests) + (page-1) * 10 + 1))):
            s_inspectQuest(quests[int(option) + (page-1) * 10])
        elif option == "m":
            s_inspectQuest(mainQuest, main=True)
        elif option == "n" and next: page += 1
        elif option == "p" and previous: page -= 1
        elif option == "B": break
        if returnTo(): return


def s_inspectQuest(quest, main=False):
    while 1:
        clear()
        print("\n -= Inspect Main Quest =-")
        displayQuest(quest, True)
        
        options(([] if main else ["Remove"]))
        option = command(False, "alphabetic", options=("" if main else "r"))
        
        if option == "r":
            pass#remove quest
        elif option == "B": break
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

        displayPlayerStats(passives=False)
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
        
        if option in tuple(map(str, range(0, len(player.passives) + (page-1) * 10 + 1))):
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


# Save and quit

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

        next = len(saves) > page*10 + 1
        previous = page != 1

        options((["Next"] if next else []) + (["Previous"] if previous else []) + ["Create", "Delete"])
        option = command(False, "optionumeric", options = "cd" + ("n" if next else "") + ("p" if previous else "") + "".join(tuple(map(str, range(0, len(saves))))))

        if option in tuple(map(str, range(0, len(saves)))):
            pickle.dump(player, open("data/saves/" + saves[int(option) + (page-1) * 10][1], "wb"))
            saves = [[pickle.load(open("data/saves/" + file, "rb")), file] for file in os.listdir("data/saves") if not file.endswith(".txt")]
            print("\n File saved successfully!")
            pressEnter()
            break
        elif option == "c": s_create()
        elif option == "d": s_delete()
        elif option == "n" and next: page += 1
        elif option == "p" and previous: page -= 1
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
        elif option == "D": pass
        elif not re.match("[\w\s]", option) or len(option) < 2:
            print("\n Your name cannot be \"" + option + "\".")
            pressEnter()
        else:
            pickle.dump(player, open("data/saves/" + option.capitalize(), "wb"))
            saves = [[pickle.load(open("data/saves/" + file, "rb")), file] for file in os.listdir("data/saves") if not file.endswith(".txt")]
            print("\n File saved successfully!")
            pressEnter()
            break
        if returnTo(): break


def s_delete():
    global saves
    page = 1
    while 1:
        clear()

        print("\n -= Delete =-\n")

        for i in range(-10 + 10*page, 10*page if 10*page < len(saves) else len(saves)):
            print(f' {i}) {saves[i][1]} | {saves[i][0].name} [Lvl {saves[i][0].level}]')

        if len(saves) == 0:
            print(" " + c("dark gray") + "- Empty -" + reset)

        next = len(saves) > page*10 + 1
        previous = page != 1

        options((["Next"] if next else []) + (["Previous"] if previous else []))
        option = command(False, "optionumeric", options = ("n" if next else "") + ("p" if previous else "") + "".join(tuple(map(str, range(0, len(saves))))))

        if option == "B": break
        elif option in tuple(map(str, range(0, len(saves) - (page-1) * 10 + 1))):
            os.remove("data/saves/" + saves[int(option) + (page-1) * 10][1])
            saves = [[pickle.load(open("data/saves/" + file, "rb")), file] for file in os.listdir("data/saves") if not file.endswith(".txt")]
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

        if option == "y": exitGame()
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
        random.seed()
        if system == "Windows":
            os.system("title=Magyka")
        else:
            orig_settings = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin)
        
        with open("map.txt") as mapFile:
            worldMap = mapFile.readlines()
        worldMap = [line.strip() for line in worldMap]
        
        saves = [[pickle.load(open("data/saves/" + file, "rb")), file] for file in os.listdir("data/saves") if not file.endswith(".txt")]

        def newPassive(name):
            session = sqlite3.connect("data/data.db")
            session.row_factory = dictFactory
            cur = session.cursor()
            passive = cur.execute('select * from passives where name="' + name + '"').fetchone()
            session.close()
            if not passive:
                print(" Error trying to load passive '" + name + "'.")
                print(" Passive doesn't exist.")
                pressEnter()
                return passive
            jsonLoads = ["effect", "tags", "turns"]
            for load in jsonLoads:
                try:
                    if passive[load]: passive[load] = json.loads(passive[load])
                except Exception as err:
                    print(" Error trying to load passive '" + name + "'.")
                    print(" Passed value: '" + passive[load] + "'.")
                    printError()
                    pressEnter()
            return passive
        session = sqlite3.connect("data/data.db")
        session.row_factory = dictFactory
        passives = [passive["name"] for passive in session.cursor().execute("select * from passives").fetchall()]
        session.close()

        def newEnchantment(name, tier, level):
            session = sqlite3.connect("data/data.db")
            session.row_factory = dictFactory
            cur = session.cursor()
            enchantment = cur.execute('select * from enchantments where name="' + name + '"').fetchone()
            session.close()
            if not enchantment:
                print(" Error trying to load enchantment '" + name + "'.")
                print(" Enchantment doesn't exist.")
                pressEnter()
                return enchantment
            jsonLoads = ["effect", "tags", "increase", "value"]
            for load in jsonLoads:
                try:
                    if enchantment[load]: enchantment[load] = json.loads(enchantment[load])
                except Exception as err:
                    print(" Error trying to load enchantment '" + name + "'.")
                    print(" Passed value: '" + enchantment[load] + "'.")
                    printError()
                    pressEnter()
            
            if enchantment["tags"] == None: enchantment["tags"] = []
            if enchantment["effect"] == None: enchantment["effect"] = []
            
            for effect in enchantment["effect"]:
                effect["value"] = effect["value"][tier]
            for i in range(len(enchantment["tags"])):
                name = enchantment["tags"][i].split(":")[0]
                values = json.loads(enchantment["tags"][i].split(":")[1])
                enchantment["tags"][i] = name + ":" + str(values[tier])
            
            if enchantment["increase"] != None: enchantment["increase"] = enchantment["increase"][tier]
            enchantment["value"] = enchantment["value"][tier]
            enchantment.update({"level": level, "tier": tier, "real name": enchantment["name"]})
            
            if tier == 0: enchantment["name"] = "Lesser " + enchantment["name"]
            elif tier == 2: enchantment["name"] = "Advanced " + enchantment["name"]
            
            for i in range(len(enchantment["tags"])):
                for j in range(level - 1):
                    if enchantment["increase"][0] == "+":
                        enchantment["tags"][i] = enchantment["tags"][i].split(":")[0] + ":" + str(int(enchantment["tags"][i].split(":")[1]) + int(enchantment["increase"][1:]))
                    elif enchantment["increase"][0] == "-":
                        enchantment["tags"][i] = enchantment["tags"][i].split(":")[0] + ":" + str(int(enchantment["tags"][i].split(":")[1]) - int(enchantment["increase"][1:]))
                    elif enchantment["increase"][0] == "*":
                        enchantment["tags"][i] = enchantment["tags"][i].split(":")[0] + ":" + str(int(enchantment["tags"][i].split(":")[1]) * float(value[1:]))
            for effect in enchantment["effect"]:
                for i in range(level - 1):
                    if enchantment["increase"][0] == "+": effect["value"] += int(enchantment["increase"][1:])
                    elif enchantment["increase"][0] == "-": effect["value"] -= int(enchantment["increase"][1:])
                    elif enchantment["increase"][0] == "*": effect["value"] = round(float(value[1:]) * effect["value"])
            
            return enchantment
        session = sqlite3.connect("data/data.db")
        session.row_factory = dictFactory
        es = [enchantment for enchantment in session.cursor().execute("select * from enchantments").fetchall()]
        enchantments = {}
        for enchantment in es:
            if enchantment["slot"] not in enchantments: enchantments.update({enchantment["slot"]: {}})
        for e in es:
            enchantments[e["slot"]].update({e["name"]: e["maxLevel"]})
        session.close()
        
        def newModifier(name):
            session = sqlite3.connect("data/data.db")
            session.row_factory = dictFactory
            cur = session.cursor()
            modifier = cur.execute('select * from modifiers where name="' + name + '"').fetchone()
            session.close()
            if not modifier:
                print(" Error trying to load modifier '" + name + "'.")
                print(" Modifier doesn't exist.")
                pressEnter()
                return modifier
            jsonLoads = ["effect", "tags"]
            for load in jsonLoads:
                try:
                    if modifier[load]: modifier[load] = json.loads(modifier[load])
                except Exception as err:
                    print(" Error trying to load modifier '" + name + "'.")
                    print(" Passed value: '" + modifier[load] + "'.")
                    printError()
                    pressEnter()
            if modifier["tags"] == None: modifier["tags"] = []
            return modifier
        session = sqlite3.connect("data/data.db")
        session.row_factory = dictFactory
        ms = [modifier for modifier in session.cursor().execute("select * from modifiers").fetchall()]
        modifiers = {}
        for modifier in ms:
            if modifier["slot"] not in modifiers:
                modifiers.update({modifier["slot"]: [m["name"] for m in ms if m["slot"] == modifier["slot"] or m["slot"] == "all"]})
        session.close()

        def newItem(name, modifier=False):
            session = sqlite3.connect("data/data.db")
            session.row_factory = dictFactory
            cur = session.cursor()
            item = cur.execute('select * from items where name="' + name + '"').fetchone()
            session.close()
            if not item:
                print(" Error trying to load item '" + name + "'.")
                print(" Item doesn't exist.")
                pressEnter()
                return item
            jsonLoads = ["effect", "tags", "enchantments"]
            for load in jsonLoads:
                try:
                    if item[load]: item[load] = json.loads(item[load])
                except Exception as err:
                    print(" Error trying to load item '" + name + "'.")
                    print(" Passed value: '" + item[load] + "'.")
                    printError()
                    pressEnter()
            if item["tags"] == None: item["tags"] = []
            if item["enchantments"] == None: item["enchantments"] = []
            if item["type"] == "equipment":
                for effect in item["effect"]:
                    if effect["type"] == "passive": effect["value"] = newPassive(effect["value"])
            for i in range(len(item["enchantments"])):
                item["enchantments"][i] = newEnchantment(item["enchantments"][i][0], item["enchantments"][i][1], item["enchantments"][i][2])
            if item["type"] == "equipment": item.update({"modifier": newModifier("Normal")})
            item["base effect"] = copy.deepcopy(item["effect"])
            item["base tags"] = copy.deepcopy(item["tags"])
            item["base value"] = item["value"]
            return item
        session = sqlite3.connect("data/data.db")
        session.row_factory = dictFactory
        items = {item["name"]: newItem(item["name"]) for item in session.cursor().execute("select * from items").fetchall()}
        session.close()

        def newEnemy(name):
            session = sqlite3.connect("data/data.db")
            session.row_factory = dictFactory
            cur = session.cursor()
            enemy = cur.execute('select * from enemies where name="' + name + '"').fetchone()
            session.close()
            if not enemy:
                print(" Error trying to load enemy '" + name + "'.")
                print(" Enemy doesn't exist.")
                pressEnter()
                return enemy
            jsonLoads = ["stats", "level", "items", "tags"]
            for load in jsonLoads:
                try:
                    if enemy[load]: enemy[load] = json.loads(enemy[load])
                except Exception as err:
                    print(" Error trying to load enemy '" + enemy["name"] + "'.")
                    print(" Passed value: '" + enemy[load] + "'.")
                    printError()
                    pressEnter()
            return Enemy(enemy)
        
        session = sqlite3.connect("data/data.db")
        session.row_factory = dictFactory
        recipes = [recipe for recipe in session.cursor().execute("select * from recipes").fetchall()]
        for recipe in recipes:
            recipe["ingredients"] = json.loads(recipe["ingredients"])
        session.close()
        
        def loadStore(location, storeType):
            return stores[location][storeType]
        
        def loadEncounter(location, area):
            return [[enemy[0]*2, newEnemy(enemy[1])] for enemy in encounters[location][area]]
    
        with open("data/encounters.json", "r") as encounterFile:
            encounters = json.load(encounterFile)
    
        with open("data/stores.json", "r") as storeFile:
            stores = json.load(storeFile)
        
        with open("data/quests.json", "r") as questFile:
            quests = json.load(questFile)
        
        with open("data/settings.json", "r+") as settingsFile:
            settings = json.load(settingsFile)
        
        if settings["fullscreen"]: fullscreen()
        
        player = Player({"weapon":newItem("Tarnished Sword"),"tome":"","head":"","chest":newItem("Patched Shirt"),"legs":newItem("Patched Jeans"),"feet":"","accessory":""}, quests["main"])
        s_mainMenu()
except Exception as err:
    printError()
    pressEnter()
    if system != "Windows": termios.tcsetattr(sys.stdin, termios.TCSADRAIN, orig_settings)
