from script.Control import control
from script.Entity import Entity, Player, Enemy
import script.Globals as Globals
from script.Item import Item
from script.Printing import printing
from script.Text import text
import atexit
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


def exit_handler():
    text.set_cursor_visible(True)
    if Globals.system != "Windows":
        control.reset_input_settings()


class Magyka:
    def __init__(self):
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
        
        self.nextScreen = ""

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
        if table == "passives":
            pass
        elif table == "enchantments":
            obj.update({"level": 1, "tier": 0, "real name": obj["name"]})
        elif table == "modifiers":
            pass
        elif table == "lootTables":
            pass
        elif table == "items":
            if obj["type"] == "equipment":
                for effect in obj["effect"]:
                    if effect["type"] == "passive":
                        effect["value"] = self.load_from_db("passives", effect["value"])
            
            for i in range(len(obj["enchantments"])):
                obj["enchantments"][i] = self.update_enchantment(self.load_from_db("enchantments", obj["enchantments"][i][0]), obj["enchantments"][i][1], obj["enchantments"][i][2])
            
            if obj["type"] == "equipment":
                obj.update({"modifier": self.load_from_db("modifiers", "Normal")})
            
            obj = Item(obj)
        elif table == "enemies":
            obj = Enemy(obj)
        
        return obj
    
    def dev_command(self, command):
        commandSplit = command.split(" ", 1)
        
        # No Argument Command Handling
        if command == "s":
            self.player.name = "Vincent"
            self.nextScreen = "camp"
        elif command == "qs":
            self.player.name = "Dev"
            self.player.gold = 999999999
            self.nextScreen = "camp"
        elif command == "q":
            sys.exit()
        elif command == "restart":
            text.clear()
            os.execv(sys.executable, ['python'] + sys.argv)
        elif command == "color":
            text.color = not text.color
        elif command == "heal":
            self.player.hp = self.player.stats["max hp"]
            self.player.mp = self.player.stats["max mp"]
        
        # Single Argument Command Handling
        elif commandSplit[0] == "exec":
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
                print("\n", err)
                control.press_enter()
        elif commandSplit[0] == "give":
            commandSplitComma = commandSplit[1].split(", ")
            try:
                self.player.add_item(self.load_from_db("items", commandSplitComma[0]), 1 if len(commandSplitComma) == 1 else commandSplitComma[1])
            except Exception as err:
                traceback.print_exc()
                control.press_enter()
        elif command != "" and command != "/C":
            print("\n That's not a command, stupid.")
            control.press_enter()


class Screen:
    def __init__(self):
        self.nextScreen = "title_screen"
        self.lastScreen = ""
        self.returnScreen = ""
        self.oldScreen = ""
        
        self.code = ""
        
        self.inspectItem = None
        self.inspectItemEquipped = False
        
        while 1:
            if self.code:
                self.handle_codes(self.code)
            
            if magyka.nextScreen:
                self.nextScreen = magyka.nextScreen
                magyka.nextScreen = ""
            
            try:
                if self.oldScreen != self.lastScreen:
                    self.oldScreen = self.lastScreen
                next_screen = getattr(self, self.nextScreen)
                self.lastScreen = self.nextScreen
            except AttributeError:
                print(f'\n Error: screen "{self.nextScreen}" does not exist.')
                control.press_enter()
                next_screen = getattr(self, self.lastScreen)
            next_screen()
    
    def handle_codes(self, option):
        if option == "/B":
            self.nextScreen = self.returnScreen
        elif option == "/D":
            command = control.get_input("command")
            magyka.dev_command(command)
        
        self.code = None
    
    # - Main Menu
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
                self.nextScreen = "continue_game"
                return
            elif option == "h":
                self.nextScreen = "help"
                return
            elif option == "o":
                self.nextScreen = "options"
                return
            else:
                self.code = option
                return
    
    def new_game(self):
        self.nextScreen = "camp"
    
    def continue_game(self):
        magyka.dev_command("give Wheat Biscuit")
        magyka.dev_command("give Iron Battleaxe")
        self.nextScreen = "camp"
    
    def help(self):
        self.nextScreen = self.returnScreen
    
    def options(self):
        self.nextScreen = self.returnScreen
    
    # - Camp
    def camp(self):
        while 1:
            self.returnScreen = "camp"
            text.clear()
            
            printing.header("Camp")
            magyka.player.show_stats(passives=False)
            
            printing.options(["Explore", "Map", "Character", "Rest", "Options"])
            option = control.get_input("alphabetic", options="emcroq", back=False)
            
            if option == "e":
                self.nextScreen = "explore"
                return
            elif option == "m":
                self.nextScreen = "map"
                return
            elif option == "c":
                self.nextScreen = "character"
                return
            elif option == "r":
                self.nextScreen = "rest"
                return
            elif option == "o":
                self.nextScreen = "options"
                return
            else:
                self.code = option
                return
    
    def explore(self):
        self.nextScreen = self.returnScreen
    
    def map(self):
        self.nextScreen = self.returnScreen
    
    def character(self):
        while 1:
            self.returnScreen = "camp"
            text.clear()
            
            printing.header("Character")
            magyka.player.show_stats()
            
            printing.options(["Inventory", "Equipment", "Quests", "Stats"])
            option = control.get_input("alphabetic", options="ieqs")
            
            if option == "i":
                self.nextScreen = "inventory"
                return
            elif option == "e":
                self.nextScreen = "equipment"
                return
            elif option == "q":
                self.nextScreen = "quests"
                return
            elif option == "s":
                self.nextScreen = "stats"
                return
            else:
                self.code = option
                return
    
    def inventory(self):
        page = 1
        while 1:
            self.returnScreen = "character"
            text.clear()
            
            printing.header("Inventory")
            print("")
            
            for i in range((page - 1) * 10, min(page * 10, len(magyka.player.inventory))):
                print(f' {str(i)[:-1]}({str(i)[-1]}) {magyka.player.inventory[i][0].name} x{magyka.player.inventory[i][1]}')
            
            if len(magyka.player.inventory) == 0:
                print(f' {text.darkgray}Empty{text.reset}')
            
            next = len(magyka.player.inventory) > page * 10
            previous = page > 1
            
            printing.options((["Next"] if next else []) + (["Previous"] if previous else []))
            option = control.get_input("optionumeric", textField=False, options=("n" if next else "") + ("p" if previous else "") + "".join(tuple(map(str, range(0, len(magyka.player.inventory))))))
            
            if option in tuple(map(str, range(0, len(magyka.player.inventory) + (page-1) * 10 + 1))):
                self.inspectItem = magyka.player.inventory[int(option) + (page - 1) * 10][0]
                self.inspectItemEquipped = False
                self.nextScreen = "inspect"
                return
            elif option == "n":
                page += 1
            elif option == "p":
                page -= 1
            else:
                self.code = option
                return
    
    def equipment(self):
        while 1:
            self.returnScreen = "character"
            text.clear()
            
            printing.header("Equipment")
            print("")
            
            for i in range(len(Globals.slotList)):
                if magyka.player.equipment[Globals.slotList[i]]:
                    print(f' {i}) {magyka.player.equipment[Globals.slotList[i]].name}')
                else:
                    print(f' {i}) {text.darkgray}Empty{text.reset}')
            
            option = control.get_input("numeric", options="".join(tuple(map(str, range(0, len(Globals.slotList))))))
            
            if option in tuple(map(str, range(0, len(Globals.slotList)))) and magyka.player.equipment[Globals.slotList[int(option)]] != "":
                self.inspectItem = magyka.player.equipment[Globals.slotList[int(option)]]
                self.inspectItemEquipped = True
                self.nextScreen = "inspect"
                return
            else:
                self.code = option
                return
    
    def inspect(self):
        while 1:
            self.returnScreen = self.oldScreen
            self.nextScreen = self.returnScreen
            text.clear()
            
            if self.inspectItemEquipped:
                self.inspectItem.update()
            magyka.player.update_stats()
            
            print(f'\n -= Inspect {self.inspectItem.type.capitalize()} =-')
            print("\n Item stats :D")
            print(f'\n Value: {text.gp} {text.reset}{self.inspectItem.value}')
            
            if self.inspectItem.type == "equipment":
                printing.options((["Unequip"] if self.inspectItemEquipped else ["Equip", "Discard"])+["More Info"])
                option = control.get_input("alphabetic", options=("u" if self.inspectItemEquipped else "ed")+"m")
            elif self.inspectItem.type == "consumable":
                printing.options((["Use"] if self.inspectItem.target == "self" else [])+["Discard"])
                option = control.get_input("alphabetic", options=("u" if self.inspectItem.target == "self" else "")+"d")
            elif self.inspectItem.type == "modifier":
                printing.options(["Use", "Discard"])
                option = control.get_input("alphabetic", options="ud")
            else:
                printing.options(["Discard"])
                option = control.get_input("alphabetic", options="d")
            
            if option == "u" and self.inspectItem.type == "equipment":
                magyka.player.unequip(self.inspectItem.slot)
                return
            elif option == "u" and self.inspectItem.type == "consumable" and self.inspectItem.target == "self":
                print("NEED USEITEM FUNCTION")
                #text, z, y = useItem(item, player)
                #for line in text:
                #    print(evalText(line))
                control.press_enter()
                if magyka.player.num_of_items(self.inspectItem.name) <= 0: return
            elif option == "u" and self.inspectItem.type == "modifier":
                s_applyModifier(self.inspectItem)
                if "infinite" not in self.inspectItem.tags: magyka.player.remove_item(self.inspectItem)
                if magyka.player.num_of_items(self.inspectItem.name) <= 0: break
            elif option == "e" and self.inspectItem.type == "equipment":
                magyka.player.equip(self.inspectItem)
                return
            elif option == "d":
                if magyka.player.num_of_items(self.inspectItem.name) > 1:
                    while 1:
                        clear()
                        header("Quantity")
                        print(f'\n Type the quantity to discard (1-{player.num_of_items(self.inspectItem.name)})')

                        option = command(True, "numeric")

                        if option == "B": break
                        elif option in tuple(map(str, range(1, magyka.player.num_of_items(self.inspectItem.name)+1))):
                            magyka.player.remove_item(self.inspectItem, int(option))
                            return
                else:
                    magyka.player.remove_item(self.inspectItem)
                    break
            else:
                self.code = option
                return
    
    def rest(self):
        self.nextScreen = self.returnScreen


if __name__ == "__main__":
    atexit.register(exit_handler)
    
    try:
        magyka = Magyka()
        magyka.player.name = "Asdf"
        screen = Screen()
    except Exception as err:
        print("")
        traceback.print_exc()
        control.press_enter()
