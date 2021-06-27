from script.Control import control
from script.Entity import Entity, Player, Enemy
import script.Globals as Globals
from script.Item import Item
from script.Screen import screen
from script.Text import text
import copy, json, math, os, pickle, random, re, sqlite3, string, sys, time, traceback


def dict_factory(cursor, row):
        # Converts sqlite return value into a dictionary with column names as keys
        d = {}
        for i, col in enumerate(cursor.description):
            d[col[0]] = row[i]
        
        return d

class Magyka:
    def __init__(self):
        text.clear()
        print("\n Loading...")
        
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
        if table == "passives": jsonLoads = ["effect", "tags", "turns"]
        elif table == "enchantments": jsonLoads = ["effect", "tags", "increase", "value"]
        elif table == "modifiers": jsonLoads = ["effect", "tags"]
        elif table == "lootTables": jsonLoads = ["drops", "tags"]
        elif table == "items": jsonLoads = ["effect", "tags", "enchantments"]
        elif table == "enemies": jsonLoads = ["stats", "level", "tags"]
        
        if not obj.get("effect"): obj["effect"] = []
        if not obj.get("tags"): obj["tags"] = []
        if not obj.get("enchantments"): obj["enchantments"] = []
        
        for jsonLoad in jsonLoads:
            if not jsonLoad in obj: continue
            try:
                if obj[jsonLoad]: obj[jsonLoad] = json.loads(obj[jsonLoad])
            except:
                print(f'\n Error: "{jsonLoad}" could not be read from "{table}.{name}".')
                print(  f'        Passed value was "{obj[jsonLoad]}".')
                control.press_enter()
        
        # Object formatting
        if table == "items":
            if obj["type"] == "equipment":
                for effect in obj["effect"]:
                    if effect["type"] == "passive": effect["value"] = self.load_from_db("passives", effect["value"])
            for i in range(len(obj["enchantments"])):
                obj["enchantments"][i] = self.update_enchantment(self.load_from_db("enchantments", obj["enchantments"][i][0]), obj["enchantments"][i][1], obj["enchantments"][i][2])
            if obj["type"] == "equipment": obj.update({"modifier": self.load_from_db("modifiers", "Normal")})
        elif table == "enchantments":
            obj.update({"level": 1, "tier": 0, "real name": obj["name"]})
        
        return obj
    
    
    def update_enchantment(self, enchantment, tier, level):
        if tier == 0: enchantment["name"] = "Lesser " + enchantment["name"]
        elif tier == 2: enchantment["name"] = "Advanced " + enchantment["name"]
        
        if enchantment["increase"] != None:
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


if __name__ == "__main__":
    magyka = Magyka()
    
    item = magyka.load_from_db("items", "Wheat Biscuit")
    
    print(item)
    
    item = Item(item)
    
    print(item)
    
    print(item.effect)
    
    control.press_enter()