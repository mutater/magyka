from script.Control import control
from script.Entity import Entity, Player, Enemy
import script.Globals as Globals
from script.Item import Item
from script.Printing import printing
from script.Text import text
import copy
import json
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


def dict_factory(cursor, row):
    # Converts sqlite return value into a dictionary with column names as keys
    d = {}
    for i, col in enumerate(cursor.description):
        d[col[0]] = row[i]

    return d


class Magyka:
    def __init__(self, screen):
        text.clear()
        
        with open("map/world map.txt") as mapFile:
            self.worldMap = mapFile.readlines()
        self.worldMap = [line.strip() for line in self.worldMap]
        
        with open("data/encounters.json", "r") as encounterFile:
            self.encounters = json.load(encounterFile)
    
        with open("data/stores.json", "r") as storeFile:
            self.stores = json.load(storeFile)
        
        with open("data/quests.json", "r") as questFile:
            self.quests = json.load(questFile)
        
        with open("data/settings.json", "r+") as settingsFile:
            self.settings = json.load(settingsFile)
        
        self.player = Player({
            "weapon": self.load_from_db("items", "Tarnished Sword"),
            "tome": "",
            "head": "",
            "chest": self.load_from_db("items", "Patched Shirt"),
            "legs": self.load_from_db("items", "Patched Jeans"),
            "feet": "",
            "accessory": ""
            }, self.quests["main"])
        
        self.screen = screen
        
        while 1:
            self.update()
            
            try:
                next_screen = getattr(self.screen, self.screen.nextScreen)
                self.screen.lastScreen = self.screen.nextScreen
            except AttributeError:
                print(f'\n Error: screen "{self.screen.nextScreen}" does not exist.')
                next_screen = getattr(self.screen, self.screen.lastScreen)
            next_screen()

    def load_from_db(self, table, name):
        # Select item from DB
        session = sqlite3.connect("data/data.db")
        session.row_factory = dict_factory
        cur = session.cursor()
        obj = cur.execute('select * from ' + table + ' where name="' + name + '"').fetchone()
        session.close()
        
        # Return if no item found
        if not obj:
            print(f'\n Error: "{table}.{name}" could not be found.')
            control.press_enter()
            return None
        
        # Load required JSON text
        if table == "passives":
            jsonLoads = ["effect", "tags", "turns"]
        elif table == "enchantments":
            jsonLoads = ["effect", "tags", "increase", "value"]
        elif table == "modifiers":
            jsonLoads = ["effect", "tags"]
        elif table == "lootTables":
            jsonLoads = ["drops", "tags"]
        elif table == "items":
            jsonLoads = ["effect", "tags", "enchantments"]
        elif table == "enemies":
            jsonLoads = ["stats", "level", "tags"]
        else:
            jsonLoads = []
        
        if not obj.get("effect"):
            obj["effect"] = []
        if not obj.get("tags"):
            obj["tags"] = []
        if not obj.get("enchantments"):
            obj["enchantments"] = []
        
        for jsonLoad in jsonLoads:
            if jsonLoad not in obj:
                continue
            try:
                if obj[jsonLoad]:
                    obj[jsonLoad] = json.loads(obj[jsonLoad])
            except ValueError:
                print(f'\n Error: "{jsonLoad}" could not be read from "{table}.{name}".')
                print(f'        Passed value was "{obj[jsonLoad]}".')
                control.press_enter()
        
        # Object formatting
        if table == "items":
            if obj["type"] == "equipment":
                for effect in obj["effect"]:
                    if effect["type"] == "passive":
                        effect["value"] = self.load_from_db("passives", effect["value"])
            for i in range(len(obj["enchantments"])):
                obj["enchantments"][i] = self.update_enchantment(self.load_from_db("enchantments", obj["enchantments"][i][0]), obj["enchantments"][i][1], obj["enchantments"][i][2])
            if obj["type"] == "equipment":
                obj.update({"modifier": self.load_from_db("modifiers", "Normal")})
        elif table == "enchantments":
            obj.update({"level": 1, "tier": 0, "real name": obj["name"]})
        
        return obj

    def handle_codes(self, option):
        if option == "/B":
            self.screen.nextScreen = self.screen.returnScreen
        elif option == "/D":
            command = control.get_input("command")
            self.dev_command(command)
        elif option == "/C":
            pass
        
        self.screen.handleCode = False
        self.screen.code = ""
    
    def dev_command(self, command):
        commandSplit = command.split(" ", 1)
        
        # No Argument Command Handling
        if command == "s":
            self.player.name = "Vincent"
            self.screen.nextScreen = "camp"
        elif command == "qs":
            self.player.name = "Dev"
            self.player.gold = 999999999
            self.screen.nextScreen = "camp"
        elif command == "restart":
            text.clear()
            os.execv(sys.executable, ['python'] + sys.argv)
        elif command == "color":
            text.color = not text.color
        
        # Single Argument Command Handling
        if commandSplit[0] == "exec":
            try:
                exec(commandSplit[1])
            except Exception as err:
                print(err)
                control.press_enter()
        elif commandSplit[0] == "execp":
            try:
                print("\n " + str(eval(commandSplit[1])))
                control.press_enter()
            except Exception as err:
                print(err)
                control.press_enter()
            
    
    def update(self):
        if self.screen.handleCode:
            self.handle_codes(self.screen.code)


class Screen:
    def __init__(self):
        self.nextScreen = "title_screen"
        self.lastScreen = ""
        self.returnScreen = ""
        
        self.handleCode = False
        self.code = ""
    
    def title_screen(self):
        while 1:
            self.returnScreen = "title_screen"
            text.clear()
            
            print("\n ", end="")
            printing.write("Welcome to the world of...\n", speed=0.01)
            
            if os.get_terminal_size()[0] >= 103:
                title = open("text/magyka title.txt", "r").read().split("\n")
                for i in range(len(title)):
                    print(text.c(["026", "012", "006", "039", "045", "019", "020", "021", "004", "027", "026", "012", "006", "039", "000", "039", "006", "012"][i], code=True) + title[i] + text.reset)
            else:
                title = open("text/magyka title small.txt", "r").read().split("\n")
                for i in range(len(title)):
                    print(text.c(["026", "026", "006", "045", "018", "004", "026", "006", "000", "039"][i], code=True) + title[i] + text.reset)
            
            printing.options(["New Game", "Continue", "Help", "Options"])
            
            option = control.get_input("alphabetic", options="ncho", back=False)
            
            if option == "n":
                self.nextScreen = "new_game"
                return
            elif option == "c":
                self.nextScreen = "continue"
                return
            elif option == "h":
                self.nextScreen = "help"
                return
            elif option == "o":
                self.nextScreen = "options"
                return
            else:
                self.handleCode = True
                self.code = option
                return


if __name__ == "__main__":
    screen = Screen()
    magyka = Magyka(screen)
