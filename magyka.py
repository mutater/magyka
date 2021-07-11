from script.Control import control
from script.Effect import Effect, Passive
from script.Entity import Entity, Player, Enemy
import script.Globals as Globals
from script.Image import Image
from script.Item import Item, Enchantment, Modifier
from script.Mapper import mapper
from script.Sound import sound
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

# TODO
"""
EVERYTHING NEEDS TO CHANGE TO NEW COORDINATE DISPLAY SYSTEM MWUHAHAHAHA
 Map Screen
 - Enemy Regions
 - Reaction time Flash Test based on enemy level
  - Fleeing or Attacking
  - Flee has escape, fear state, caught
  - Attack has surprise attack, normal battle, or enemy surprise attack
 - Random encounter mode toggle
 - Chance of random event occuring
Inspect Screen
 - More Stats showing enchantment and modifier effects of items
Inn Screen
 - Random Quests
 - Premade Quests
 - Gambling
Pages and Map
 - Keybindings
  - Up
  - Down
  - Left
  - Right
  - Interact
Export function on BaseClass
"""


def dict_factory(cursor, row):
    # Converts sqlite return value into a dictionary with column names as keys
    d = {}
    for i, col in enumerate(cursor.description):
        d[col[0]] = row[i]

    return d


def exit_handler(*args):
    magyka.save_game()
    text.set_cursor_visible(True)
    if Globals.system != "Windows":
        control.reset_input_settings()


class Magyka:
    def __init__(self):
        text.clear()
        
        with open("data/portals.json") as portalFile:
            self.mapPortals = json.load(portalFile)
        
        with open("data/encounters.json", "r") as encounterFile:
            self.encounters = json.load(encounterFile)
    
        with open("data/stores.json", "r") as storeFile:
            self.stores = json.load(storeFile)
        
        with open("data/quests.json", "r") as questFile:
            self.quests = json.load(questFile)
        
        with open("data/settings.json", "r+") as settingsFile:
            self.settings = json.load(settingsFile)
        
        session = sqlite3.connect("data/data.db")
        session.row_factory = dict_factory
        cur = session.cursor()
        self.recipes = cur.execute('select * from recipes').fetchall()
        session.close()
        
        for i in range(len(self.recipes)):
            self.recipes[i]["ingredients"] = json.loads(self.recipes[i]["ingredients"])
        
        self.nextScreen = ""
        self.inspectItem = None
        self.purchaseItem = None
        self.craftItem = None
        self.craftRecipe = None
        self.sellItem = None
        self.inspectPassive = None
        self.battleEnemy = None
        self.itemLog = None
        self.hunt = False
        
        self.saves = []
        
        for file in os.listdir("saves"):
            if not file.endswith(".txt"):
                try:
                    with open("saves/" + file, "rb") as saveFile:
                        self.saves.append(pickle.load(saveFile))
                except FileNotFoundError:
                    pass
    
    def init_player(self):
        self.player = Player({"mainQuests": self.quests["main"]})
    
    def load_from_db(self, table, name, **kwargs):
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
            jsonLoads = ["effect", "tags", "increase", "valueIncrease"]
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
            obj["tags"] = {}
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
        if "effect" in obj:
            for i in range(len(obj["effect"])):
                obj["effect"][i] = Effect(obj["effect"][i])
        
        if table == "passives":
            obj = Passive(obj)
        elif table == "enchantments":
            obj.update({"level": kwargs.get("level", 1), "tier": kwargs.get("tier", 0), "baseName": obj["name"]})
            if "passive" in obj["tags"]:
                for i in range(len(obj["tags"]["passive"])):
                    obj["tags"]["passive"][i] = self.load_from_db("passives", obj["tags"]["passive"][i])
        elif table == "modifiers":
            for tag in obj["tags"]:
                if tag == "passive":
                    obj["tags"][tag] = {"passive": self.load_from_db("passives", obj["tags"][tag])}
            obj = Modifier(obj)
        elif table == "lootTables":
            pass
        elif table == "items":
            try:
                if "effect" in obj and obj["effect"]:
                    for effect in obj["effect"]:
                        if effect.type == "passive":
                            passives = []
                            for passive in effect.passive:
                                passives.append(self.load_from_db("passives", passive))
                            effect.passive = passives
                        elif effect.passive:
                            passives = []
                            for passive in effect.passive:
                                passives.append(self.load_from_db("passives", passive))
                            effect.passive = passives
                
                for i in range(len(obj["enchantments"])):
                    level, tier = obj["enchantments"][i][1], obj["enchantments"][i][2]
                    obj["enchantments"][i] = Enchantment(self.load_from_db("enchantments", obj["enchantments"][i][0]))
                    obj["enchantments"][i].update(level, tier)
                
                if obj["type"] == "equipment":
                    obj.update({"modifier": self.load_from_db("modifiers", "Normal")})
                
                obj = Item(obj)
            except:
                print(f'\n Error: "{obj["name"]} could not be read."\n')
                traceback.print_exc()
                control.press_enter()
                obj = None
        elif table == "enemies":
            obj = Enemy(obj)
        
        return obj
    
    def dev_command(self, command):
        commandSplit = command.split(" ", 1)
        
        # No Argument Command Handling
        if command == "s":
            self.init_player()
            self.player.name = "Vincent"
            self.player.saveId = 69420
            self.nextScreen = "camp"
            return True
        elif command == "qs":
            self.init_player()
            self.player.name = "Dev"
            self.player.saveId = 69420
            self.player.gold = 999999999
            self.dev_command("give all")
            self.nextScreen = "camp"
            return True
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
        elif command == "buy":
            self.player.add_item(self.purchaseItem)
        elif command == "map":
            self.worldMap = mapper.get_text(mapper.mapColors, "map/world map.png", "map/world map.txt")
            self.worldMapLevel = mapper.get_text(mapper.levelColors, "map/world map level.png", "map/world map level.txt")
            self.worldMapRegion = mapper.get_text(mapper.regionColors, "map/world map region.png", "map/world map region.txt")
        elif command == "kill":
            self.battleEnemy.hp = 0
        elif command == "test":
            Image("item/Copper Sword").show_at_origin()
            control.press_enter()
        
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
                if commandSplitComma[0] == "all":
                    session = sqlite3.connect("data/data.db")
                    session.row_factory = dict_factory
                    devItems = [item["name"] for item in session.cursor().execute("select * from items").fetchall()]
                    for item in devItems:
                        self.player.add_item(self.load_from_db("items", item))
                    session.close()
                else:
                    self.player.add_item(self.load_from_db("items", commandSplitComma[0]), 1 if len(commandSplitComma) == 1 else commandSplitComma[1])
            except Exception:
                traceback.print_exc()
                control.press_enter()
        elif commandSplit[0] == "equip":
            try:
                item = self.load_from_db("items", commandSplit[1])
                self.player.equip(item)
            except Exception:
                traceback.print_exc()
                control.press_enter()
        elif commandSplit[0] == "enchant":
            commandSplitComma = commandSplit[1].split(", ")
            try:
                self.inspectItem.enchant(self.load_from_db("enchantments", commandSplitComma[0], tier=commandSplitComma[1], level=commandSplitComma[2]))
            except Exception:
                traceback.print_exc()
                control.press_enter()
        elif commandSplit[0] == "fight":
            self.battleEnemy = self.load_from_db("enemies", commandSplit[1])
            self.nextScreen = "battle"
            return True
        elif command != "" and command != "/C":
            print("\n That's not a command, stupid.")
            control.press_enter()
    
        return False
    
    def save_game(self):
        fileName = self.player.name + str(self.player.saveId)
        with open("saves/" + fileName, "wb+") as saveFile:
            pickle.dump(self.player, saveFile)
    
    def react_flash(self):
        time.sleep(0.1)
        text.clear()
        text.fill_screen("light red")
        time.sleep(0.02)
        text.clear()
        return control.time_keypress()
    
    def load_encounter(self, level=1):
        enemies = copy.deepcopy(self.encounters[self.player.location])
        weight = 0
        minLevel = 0
        if self.player.level - 2 > 0:
            minLevel = self.player.level - 2
        level = random.randint(minLevel, 2) + self.player.level
        
        print(enemies)
        
        for i in range(len(enemies)-1, -1, -1):
            enemy = enemies[i][1] = self.load_from_db("enemies", enemies[i][1])
            if enemy.level[1] < level:
                enemies.pop(i)
                continue
            
            if level - enemy.level[0] > 1:
                enemy.levelDifference = level - enemy.level[0]
            else:
                enemy.levelDifference = 0
            
            enemy.level = max(min(level, enemy.level[1]), enemy.level[0])
            
            if enemy.level - self.player.level > 0:
                enemies[i][0] -= (enemy.level - self.player.level) * 50
            if enemies[i][0] <= 0:
                enemies[i][0] = 1
            
            for stat in enemy.baseStats:
                if stat in ("strength", "vitality", "intelligence", "crit", "hit", "dodge"):
                    enemy.baseStats[stat] += round(0.5 * enemy.levelDifference)
                elif stat in ("max hp", "max mp"):
                    enemy.baseStats[stat] += round(enemy.baseStats[stat] * 0.1 * enemy.levelDifference)
            enemy.update_stats()
            enemies[i][0] += weight
            weight += enemies[i][0] - weight
        
        enemies = dict(enemies[::-1])
        
        print(enemies)
        control.press_enter()
        
        try:
            enemyNum = random.randint(1, weight)
        except:
            self.battleEnemy = None
            return
        
        for enemy in enemies:
            if enemyNum <= enemy:
                self.battleEnemy = enemies[enemy]


class Screen:
    def __init__(self):
        self.nextScreen = "title_screen"
        self.lastScreen = ""
        self.returnScreen = ""
        self.oldScreen = ""
        self.storeType = ""
        self.page = 1
        
        magyka.inspectItemEquipped = False
        
        while 1:
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
    
    def code(self, option):
        if option == "/B":
            self.nextScreen = self.returnScreen
            return True
        elif option == "/D":
            command = control.get_input("command")
            return magyka.dev_command(command)
        
        return False
    
    # - Main Menu
    def title_screen(self):
        while 1:
            self.returnScreen = "title_screen"
            text.clear()
            
            print("\n ", end="")
            print("Welcome to the world of...\n")
            
            if os.get_terminal_size()[0] >= 103:
                title = open("text/magyka title.txt", "r").read().split("\n")
                for i in range(len(title)):
                    print(text.cc(["026", "012", "006", "039", "045", "019", "020", "021", "004", "027", "026", "012", "006", "039", "000", "039", "006", "012"][i]) + title[i] + text.reset)
            else:
                title = open("text/magyka title small.txt", "r").read().split("\n")
                for i in range(len(title)):
                    print(text.cc(["026", "026", "006", "045", "018", "004", "026", "006", "000", "039"][i]) + title[i] + text.reset)
            
            text.options(["New Game", "Continue", "Help", "Options"])
            
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
            elif self.code(option):
                return

    def new_game(self):
        self.nextScreen = "camp"
        # STRING = NEWGAMETEXT
        i = 0
        delay = speed
        while i < len(string):
            if string[i:i+2] == "0m":
                print(text.reset, end="")
                i += 1
            elif string[i:i+5] == "38;5;":
                print("\x1b[" + string[i:i+10], end="")
                i += 9
            elif string[i] == "#":
                control.press_enter()
                delay = speed
            elif string[i] == "<":
                text.clear()
                delay = speed
            else:
                print(string[i], end="")
            
            time.sleep(delay)
            
            if control.get_key() == "enter":
                delay = 0
            
            sys.stdout.flush()
            i += 1
        
        print("")
    
    def continue_game(self):
        while 1:
            self.returnScreen = "title_screen"
            text.clear()
            Image("background").show_at_origin()
            Image("screen/continue").show_at_description()
            text.header("Continue")
            
            for i in range(len(magyka.saves)):
                text.print_at_loc(f'({i}) {text.title(magyka.saves[i].name, magyka.saves[i].level)}', 3 + i, 4)
            
            if len(magyka.saves) == 0:
                text.print_at_loc(f'{text.darkgray}Empty{text.reset}', 3, 4)
                delOption = ""
            else:
                delOption = "d"
            
            if delOption:
                print("")
                text.options(["Delete"])
            
            option = control.get_input("optionumeric", textField=False, options=delOption+"".join(tuple(map(str, range(0, len(magyka.saves))))))
            
            if option in tuple(map(str, range(0, len(magyka.saves)))):
                magyka.init_player()
                magyka.player = magyka.saves[int(option)]
                self.nextScreen = "camp"
                self.returnScreen = "camp"
                return
            elif option == "d":
                self.nextScreen = "delete_save"
                return
            elif self.code(option):
                return
    
    def delete_save(self):
        while 1:
            self.returnScreen = "continue_game"
            text.clear()
            Image("background").show_at_origin()
            Image("screen/continue").show_at_description()
            text.header("Delete")
            
            for i in range(len(magyka.saves)):
                text.print_at_loc(f'({i}) {text.title(magyka.saves[i].name, magyka.saves[i].level)}', 3 + i, 4)
            
            if len(magyka.saves) == 0:
                text.print_at_loc(f'{text.darkgray}Empty{text.reset}', 3, 4)
            
            option = control.get_input("numeric", textField=False, options="".join(tuple(map(str, range(0, len(magyka.saves))))))
            
            if option in tuple(map(str, range(0, len(magyka.saves)))):
                save = magyka.saves[int(option)]
                os.remove("saves/" + save.name + str(save.saveId))
                magyka.saves.pop(int(option))
                return
            elif self.code(option):
                return
    
    def help(self):
        self.nextScreen = self.returnScreen
    
    def options(self):
        self.nextScreen = self.returnScreen
    
    # - Camp
    def camp(self):
        while 1:
            self.returnScreen = "camp"
            text.clear()
            Image("background").show_at_origin()
            Image("screen/camp").show_at_description()
            text.header("Camp")
            text.move_cursor(1, 1)
            magyka.player.show_stats()
            
            text.options(["Map", "Character", "Rest", "Options"])
            option = control.get_input("alphabetic", options="mcroq", silentOptions="r", back=False)
            
            if option == "m":
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
            elif self.code(option):
                return
    
    def battle(self):
        magyka.itemLog = []
        if type(magyka.battleEnemy.level) is list:
            magyka.battleEnemy.level = magyka.battleEnemy.level[0]
        magyka.battleEnemy.hp = magyka.battleEnemy.stats["max hp"]
        magyka.battleEnemy.mp = magyka.battleEnemy.stats["max mp"]
        
        text.clear()
        Image("background").show_at_origin()
        
        # Player
        def print_player():
            text.print_at_loc(text.title(magyka.player.name, magyka.player.level), 3, 4)
            text.print_at_loc(text.bar(magyka.player.hp, magyka.player.stats["max hp"], "red", length=40, number=True), 4, 5)
            text.print_at_loc(text.bar(magyka.player.mp, magyka.player.stats["max mp"], "blue", length=40, number=True), 5, 5)
        
        # Enemy
        def print_enemy():
            text.print_at_loc(text.title(magyka.battleEnemy.name, magyka.battleEnemy.level), 3, 84)
            Image("enemy/" + magyka.battleEnemy.name).show_at_description()
            
            text.print_at_loc(text.bar(magyka.battleEnemy.hp, magyka.battleEnemy.stats["max hp"], "red"), 24, 85)
            text.print_at_loc(f' {magyka.battleEnemy.hp}/{magyka.battleEnemy.stats["max hp"]}', 25, 85)
            text.print_at_loc(text.bar(magyka.battleEnemy.mp, magyka.battleEnemy.stats["max mp"], "blue"), 27, 85)
            text.print_at_loc(f' {magyka.battleEnemy.mp}/{magyka.battleEnemy.stats["max mp"]}', 28, 85)
        
        print_player()
        print_enemy()
        
        while 1:
            while 1:
                usedItem = False
                magyka.player.guard = ""
                over = False
                
                if magyka.player.equipment.get("tome") and magyka.player.mp >= magyka.player.equipment["tome"].mana:
                    magic = True
                else:
                    magic = False
                
                text.clear_main()
                print_player()
                
                print("")
                text.options([(text.darkgray if not magic else "") + "Magic", "Attack", "Guard", "Item", "Cede"])
                option = control.get_input("alphabetic", options="agic" + ("m" if magic else ""), silentOptions="amgc", back=False, showText=False)
                
                if option == "a":
                    sound.play_sound(["attack", "slash"])
                    magyka.player.attack(magyka.battleEnemy)
                    break
                elif option == "m":
                    magyka.player.attack(magyka.battleEnemy, type="magic")
                    break
                elif option == "g":
                    guardState = random.randint(1, 5)
                    if guardState <= 3:
                        magyka.player.guard = "deflect"
                    elif guardState == 4:
                        magyka.player.guard = "block"
                    else:
                        magyka.player.guard = "counter"
                    print(f' {magyka.player.name} lowers into a defensive stance.')
                    break
                elif option == "i":
                    self.page = 1
                    usedItem = False
                    while 1:
                        text.clear()
                        Image("background").show_at_origin()
                        Image("screen/Inventory").show_at_description()
                        text.header("Inventory")
                        print("")
                        
                        itemList = []
                        for item in magyka.player.inventory:
                            if item[0].type == "consumable":
                                itemList.append(item)
                        
                        for i in range((self.page - 1) * 10, min(self.page * 10, len(itemList))):
                            item = itemList[i]
                            if i >= 100:
                                just = ""
                            elif i >= 10:
                                just = " "
                            else:
                                just = "  "
                            text.print_at_loc(f'{str(i)[:-1]}({str(i)[-1]}) {just}{item[0].get_name(True, item[1])}', 3 + int(str(i)[-1]), 4)
                        
                        if len(itemList) == 0:
                            text.print_at_loc(f'{text.darkgray}No Consumables{text.reset}', 3, 4)
                        
                        print("")
                        
                        next = len(itemList) > self.page * 10
                        previous = self.page > 1
                        
                        text.options((["Next"] if next else []) + (["Previous"] if previous else []))
                        option = control.get_input("optionumeric", textField=False, options=("n" if next else "")+("p" if previous else "")\
                        +"".join(tuple(map(str, range(0, len(itemList))))))
                        
                        if option in tuple(map(str, range(0, len(itemList) + (self.page-1) * 10 + 1))):
                            item = itemList[int(option) + (self.page - 1) * 10][0]
                            while 1:
                                text.clear()
                                Image("background").show_at_origin()
                                Image("item/" + item.name).show_at_description()
                                text.header("Use Item")
                                
                                text.move_cursor(3, 4)
                                item.show_stats()
                                
                                text.options(["Use"])
                                option = control.get_input("alphabetic", options="u", silentOptions="u")
                                
                                if option == "u":
                                    usedItem = True
                                    
                                    text.clear()
                                    Image("background").show_at_origin()
                                    print_enemy()
                                    print_player()
                                    print("")
                                    
                                    if item.target == "self":
                                        item.use(magyka.player, magyka.player)
                                    else:
                                        item.use(magyka.player, magyka.battleEnemy)
                                    
                                    if not item.tags.get("infinite"):
                                        magyka.player.remove_item(item)
                                    
                                    itemFound = False
                                    for i in magyka.itemLog:
                                        if i[0].name == item.name:
                                            i[1] += 1
                                            itemFound = True
                                            break
                                    if not itemFound:
                                        magyka.itemLog.append([item, 1])
                                    
                                    break
                                elif self.code(option):
                                    break
                            break
                        elif option == "n":
                            self.page += 1
                        elif option == "p":
                            self.page -= 1
                        elif self.code(option):
                            break
                    if usedItem:
                        break
                elif option == "c":
                    pass # FLEEING
                elif self.code(option):
                    break
            
            print_enemy()
            
            control.press_enter()
            
            if magyka.battleEnemy.hp <= 0:
                self.nextScreen = "victory"
                return
            elif magyka.player.hp <= 0:
                self.nextScreen = "defeat"
                return
            
            text.fill_rect("", 16, 3, 74, 13)
            text.move_cursor(16, 1)
            
            sound.play_sound(["hit", "hit2"])
            magyka.battleEnemy.attack(magyka.player)
            
            print_player()
            
            control.press_enter()
            text.fill_rect("", 16, 3, 74, 11)
            
            if magyka.battleEnemy.hp <= 0:
                self.nextScreen = "victory"
                return
            elif magyka.player.hp <= 0:
                self.nextScreen = "defeat"
                return
    
    def victory(self):
        text.clear()
        Image("background").show_at_origin()
        Image("enemy/"+magyka.battleEnemy.name).show_at_description()
        text.header("Victory")
        sound.play_sound("victory")
        # UPDATE PLAYER QUESTS
        
        levelDifference = magyka.battleEnemy.level - magyka.player.level
        
        if levelDifference == 0:
            lootModifier = 1
        else:
            lootModifier = max(round(1.25 ** levelDifference, 2), 0.6)
        
        xp = math.ceil(magyka.battleEnemy.xp * lootModifier)
        gold = math.ceil(random.randint(math.ceil(magyka.battleEnemy.gold*0.9), math.ceil(magyka.battleEnemy.gold*1.1)) * lootModifier)
        items = magyka.load_from_db("lootTables", magyka.battleEnemy.name)["drops"]
        
        for i in range(len(items)-1, -1, -1):
            items[i][0] = magyka.load_from_db("items", items[i][0])
            if random.randint(1, 100) <= items[i][2]:
                if type(items[i][1]) is list:
                    items[i][1] = random.randint(items[i][1][0], items[i][1][1])
                magyka.player.add_item(items[i][0], items[i][1])
            else:
                items.pop(i)
        magyka.player.gold += gold
        magyka.player.xp += xp
        magyka.player.level_up()
        
        text.print_at_loc(f'Obtained: (x{lootModifier} Loot Modifier)', 3, 4)
        for i in range(len(items)):
            text.print_at_loc(f'- {items[i][0].get_name(True, items[i][1])}', 4 + i, 5)
        
        print("")
        text.slide_cursor(0, 4)
        print(f'- {text.gp}{text.reset} {gold}')
        text.slide_cursor(0, 4)
        print(f'- {text.xp}{text.reset} {xp}')
        
        print("")
        if magyka.itemLog:
            text.slide_cursor(0, 3)
            print("Items used:")
            for item in magyka.itemLog:
                text.slide_cursor(0, 4)
                print(f'- {item[0].get_name().ljust(28)} x{item[1]}')
        else:
            text.slide_cursor(0, 3)
            print(f'Items used: {text.darkgray}None{text.reset}')
        # SHOW COMPLETED QUESTS
        
        control.press_enter()
        self.nextScreen = "camp"
    
    def defeat(self):
        text.clear()
        text.header("Defeat")
        Image("background").show_at_origin()
        Image("enemy/"+magyka.battleEnemy.name).show_at_description()
        sound.play_sound("defeat")
        text.move_cursor(3, 4)
        print("Defeated by:")
        print("")
        magyka.battleEnemy.show_stats(gpxp=False)
        
        print("")
        if magyka.itemLog:
            text.slide_cursor(0, 3)
            print("Items used:")
            for item in magyka.itemLog:
                text.slide_cursor(0, 4)
                print(f'- {item[0].get_name().ljust(28)} x{item[1]}')
        else:
            text.slide_cursor(0, 3)
            print(f'Items used: {text.darkgray}None{text.reset}')
        
        magyka.itemLog = []
        text.slide_cursor(1, 3)
        print(f'You died, ', end="")
        magyka.player.add_passive(magyka.load_from_db("passives", "Charon's Curse"))
        magyka.player.hp = 1
        magyka.player.mp = 0
        
        control.press_enter()
        self.nextScreen = "camp"
    
    # - Map
    def map(self):
        mapName = "magyka"
        mapTiles = mapper.get_text(None, "image/map/" + mapName + ".png")
        mapCollision = mapper.get_text(None, "image/map/" + mapName + " collision.png")
        text.clear()
        Image("map background").show_at_origin()
        text.header(mapName.title(), row=3, col=3, w=38)
        while 1:
            self.returnScreen = "camp"
            
            mapHeight = 28
            mapWidth = 38
            
            if len(mapTiles[0]) < mapWidth:
                mapWidth = len(mapTiles[0])
            if len(mapTiles) < mapHeight:
                mapHeight = len(mapTiles)
            
            mapTop = 2
            mapLeft = 43
            
            portal = False
            if magyka.mapPortals.get(mapName):
                for p in magyka.mapPortals[mapName]:
                    if p[0] == magyka.player.x and p[1] == magyka.player.y:
                        portal = p
            
            top = magyka.player.y - mapHeight // 2
            bottom = magyka.player.y + mapHeight // 2
            left = magyka.player.x - mapWidth // 2
            right = magyka.player.x + mapWidth // 2
            
            if top < 0:
                top = 0
            if bottom > len(mapTiles):
                bottom = len(mapTiles)
            if left < 0:
                left = 0
            if right > len(mapTiles[0]):
                right = len(mapTiles[0])
            
            text.clear_main_small()
            text.move_cursor(5, 4)
            print(text.reset + "Use WASD to move.")
            text.options(["Hunt"] + (["Enter"] if portal else []))
            text.slide_cursor(1, 3)
            
            print(f'Hunting: {"True" if magyka.hunt else "False"}')
            
            for y in range(top, bottom):
                text.move_cursor(mapTop + y - top, mapLeft)
                for x in range(left, right):
                    tile = mapTiles[y][x]
                    
                    if x == magyka.player.x and y == magyka.player.y:
                        print(text.reset + "<>", end="")
                        if x != right:
                            print(text.rgb(mapTiles[y][x + 1], back=True), end="")
                        continue
                    
                    if x > left and tile == mapTiles[y][x - 1]:
                        tileText = "  "
                    else:
                        tileText = text.rgb(tile, back=True) + "  "
                    
                    print(tileText, end="")
            
            option = control.get_input("alphabetic", options="wasdh"+("e" if portal else ""), silentOptions="wasd", showText=False)
            
            moveX = 0
            moveY = 0
            
            if option == "w" and mapCollision[magyka.player.y-1][magyka.player.x] != "0;0;0":
                moveY -= 1
            elif option == "a" and mapCollision[magyka.player.y][magyka.player.x-1] != "0;0;0":
                moveX -= 1
            elif option == "s" and mapCollision[magyka.player.y+1][magyka.player.x] != "0;0;0":
                moveY += 1
            elif option == "d" and mapCollision[magyka.player.y][magyka.player.x+1] != "0;0;0":
                moveX += 1
            
            if moveX or moveY:
                magyka.player.x += moveX
                magyka.player.y += moveY
                
                if random.randint(1, (20 if magyka.hunt else 100)) == 1:
                    responseTime = magyka.react_flash()
                    if responseTime <= 320:
                        self.nextScreen = "map"
                        return
                    elif responseTime <= 450:
                        magyka.player.add_passive(magyka.load_from_db("passives", "Shaken"))
                        self.nextScreen = "map"
                        return
                    else:
                        magyka.load_encounter(mapCollision[magyka.player.x][magyka.player.y].split(";")[0])
                        self.nextScreen = "battle"
                        return
            
            if option == "e":
                if portal[2] == "map":
                    mapName = portal[3]
                    magyka.player.x = portal[4]
                    magyka.player.y = portal[5]
                elif portal[2] == "town":
                    magyka.player.location = portal[3]
                    self.nextScreen = "town"
                    return
                elif portal[2] == "location":
                    magyka.player.location = portal[3]
                    self.nextScreen = "location"
                    return
            elif option == "h":
                magyka.hunt = not magyka.hunt
            elif self.code(option):
                return
    
    def town(self):
        while 1:
            self.returnScreen = "map"
            text.clear()
            Image("background").show_at_origin()
            Image("screen/Town").show_at_description()
            text.header(magyka.player.location.title())
            
            text.options(["Inn", "General Store", "Blacksmith", "Arcanist", "Flea Market"])
            option = control.get_input("alphabetic", options="igbaf")
            
            if option in ("gba"):
                self.nextScreen = "store"
                self.page = 1
            
            if option == "i":
                self.nextScreen = "inn"
                return
            elif option == "g":
                self.storeType = "general"
                return
            elif option == "b":
                self.storeType = "blacksmith"
                return
            elif option == "a":
                self.storeType = "arcanist"
                return
            elif option == "f":
                self.nextScreen = "market"
                return
            elif self.code(option):
                return
    
    def inn(self):
        while 1:
            self.returnScreen = "town"
            text.clear()
            
            text.header("Inn")
            
            price = 5 + magyka.player.level * 2

            print(f'\n Price to rest: {text.gp}{text.reset} {price}')
            
            text.options(["Rest", text.darkgray + "Quest", text.darkgray + "Gamble"])
            option = control.get_input("alphabetic", options = "r")
            
            if option == "r":
                if magyka.player.gold >= price:
                    sound.play_sound("rest")
                    magyka.player.gold -= price
                    magyka.player.hp = magyka.player.stats["max hp"]
                    magyka.player.mp = magyka.player.stats["max mp"]
                    magyka.player.add_passive(magyka.load_from_db("passives", "Well Rested"))
                    print("\n You fell well rested. HP and MP restored to full.")
                    control.press_enter()
                else:
                    print(f'\n {text.lightred} You do not have enough gold to rest.')
                    control.press_enter()
            elif self.code(option):
                return
    
    def store(self):
        while 1:
            self.returnScreen = "town"
            text.clear()
            Image("background").show_at_origin()
            Image("screen/Store").show_at_description()
            text.header(self.storeType.capitalize())
            
            storeData = magyka.stores[magyka.player.location][self.storeType]
            itemList = []
            
            for item in storeData["inventory"]:
                try:
                    itemList.append(magyka.load_from_db("items", item))
                except:
                    pass
            
            next = len(itemList) > self.page * 10
            previous = self.page > 1
            
            if self.storeType != "general":
                print("\n Equipment:")
                for i in range(len(Globals.slotList)):
                    if magyka.player.equipment[Globals.slotList[i]] != "": print(f'  - {magyka.player.equipment[Globals.slotList[i]].get_name()}')
            print(f'\n {text.gp}{text.reset} {magyka.player.gold}\n')
            
            for i in range(-10 + 10*self.page, 10*self.page if 10*self.page < len(itemList) else len(itemList)):
                if itemList[i].type in Globals.stackableItems:
                    quantity = True
                else:
                    quantity = False
                print(f' {i}) {itemList[i].get_name(effect=True)}{" x1" if quantity else ""} {text.gp}{text.reset} {itemList[i].value}')
            
            if len(itemList) == 0:
                print(f' {text.darkgray}Empty{text.reset}')
            
            text.options((["Next"] if next else [])+(["Previous"] if previous else [])+(["Reforge"] if self.storeType == "blacksmith" else [])+["Crafting"])
            option = control.get_input("optionumeric", options=("n" if next else "")+("p" if previous else "")+("r" if self.storeType == "blacksmith" else "")+"c"+"".join(tuple(map(str, range(0, len(itemList))))), textField=False)
            
            if option in tuple(map(str, range(0, len(itemList) + (self.page-1) * 10 + 1))):
                magyka.purchaseItem = itemList[int(option) + (self.page-1) * 10]
                self.nextScreen = "purchase"
                return
            elif option == "r":
                self.nextScreen = "reforging"
                return
            elif option == "c":
                self.page = 1
                self.nextScreen = "crafting"
                return
            elif option == "n":
                self.page += 1
            elif option == "p":
                self.page -= 1
            elif self.code(option):
                return
    
    def purchase(self):
        while 1:
            self.returnScreen = "store"
            self.nextScreen = self.returnScreen
            text.clear()
            
            text.header("Purchase " + magyka.purchaseItem.name)
            
            magyka.purchaseItem.show_stats()
            
            print(f'\n {text.gp}{text.reset} {magyka.player.gold}')
            print(f'\n Currently owned: {magyka.player.num_of_items(magyka.purchaseItem.name)}')
            print(f' Type the quantity of items to be purchased ({magyka.player.gold // magyka.purchaseItem.value} can be bought).')
            
            option = control.get_input("numeric")
            
            print("")
            
            try:
                option = int(option)
            except:
                pass
            
            if type(option) is int:
                if option * magyka.purchaseItem.value <= magyka.player.gold:
                    sound.play_sound("coin")
                    magyka.player.add_item(magyka.purchaseItem, option)
                    magyka.player.gold -= option * magyka.purchaseItem.value
                    
                    if magyka.purchaseItem.type in Globals.stackableItems:
                        quantity = True
                    else:
                        quantity = False
                    print(f' {magyka.purchaseItem.get_name()}{" x" + str(option) if quantity else ""} added to your inventory!')
                    
                    control.press_enter()
                    return
                else:
                    if magyka.purchaseItem.type in Globals.stackableItems:
                        quantity = True
                    else:
                        quantity = False
                    print(f' {text.lightred} You cannot buy that many.')
                    control.press_enter()
                    return
            elif self.code(option):
                return
    
    def crafting(self):
        while 1:
            self.returnScreen = "store"
            text.clear()
            
            text.header("Crafting")
            print("")
            
            recipes = []
            for recipe in magyka.recipes:
                addRecipe = False
                for item in recipe["ingredients"]:
                    if magyka.player.num_of_items(item[0]) > 0:
                        addRecipe = True
                        break
                
                if addRecipe and recipe["type"] == self.storeType:
                    recipes.append(recipe)
            
            for i in range(-10 + 10*self.page, 10*self.page if 10*self.page < len(recipes) else len(recipes)):
                item = magyka.load_from_db("items", recipes[i]["result"])
                if item.type in Globals.stackableItems:
                    quantity = True
                else:
                    quantity = False
                print(f' {str(i)[:-1]}({str(i)[-1]}) {item.get_name()}{" x" + str(recipe["quantity"]) if quantity else ""}')
            
            if len(recipes) == 0:
                print(f' {text.darkgray}No Items Craftable{text.reset}')
            
            next = len(recipes) > self.page * 10
            previous = self.page > 1
            
            text.options((["Next"] if next else [])+(["Previous"] if previous else []))
            option = control.get_input("optionumeric", options=("N" if next else "")+("p" if previous else "")+"".join(tuple(map(str, range(0, len(recipes))))))
            
            if option in tuple(map(str, range(0, len(recipes) + (self.page-1) * 10 + 1))):
                magyka.craftRecipe = recipes[int(option) + (self.page-1) * 10]
                self.nextScreen = "craft"
                return
            elif option == "n":
                self.page += 1
            elif option == "p":
                self.page -= 1
            elif self.code(option):
                return
    
    def craft(self):
        while 1:
            self.returnScreen = "crafting"
            self.nextScreen = self.returnScreen
            text.clear()
            
            text.header("Craft " + magyka.craftRecipe["result"])
            
            magyka.craftItem = magyka.load_from_db("items", magyka.craftRecipe["result"])
            
            magyka.craftItem.show_stats()
            print(f'\n Value: {text.gp}{text.reset} {magyka.craftItem.value}')
            
            craftable = True
            numCraftable = 99999999
            print("\n Requires:\n")
            for i in range(len(magyka.craftRecipe["ingredients"])):
                playerIngredientCount = magyka.player.num_of_items(magyka.craftRecipe["ingredients"][i][0])
                recipeIngredientCount = magyka.craftRecipe["ingredients"][i][1]
                if playerIngredientCount < recipeIngredientCount:
                    craftable = False
                    numCraftable = 0
                elif playerIngredientCount // recipeIngredientCount < numCraftable:
                    numCraftable = playerIngredientCount // recipeIngredientCount
                ingredient = magyka.load_from_db("items", magyka.craftRecipe["ingredients"][i][0])
                print(f' {recipeIngredientCount}x {ingredient.get_name()} ({playerIngredientCount}/{recipeIngredientCount})')
            
            if magyka.craftItem.type == "equipment" and craftable:
                numCraftable = 1
            
            print(f'\n Type the quantity of items to be crafted ({numCraftable} craftable)')
            option = control.get_input("numeric")
            
            print("")
            
            try:
                option = int(option)
            except:
                pass
            
            if type(option) is int:
                if option <= numCraftable:
                    for item in magyka.craftRecipe["ingredients"]:
                        magyka.player.remove_item(magyka.load_from_db("items", item[0]), item[1])
                    magyka.player.add_item(magyka.craftItem, magyka.craftRecipe["quantity"] * option)
                    
                    if magyka.craftItem.type in Globals.stackableItems:
                        quantity = True
                    else:
                        quantity = False
                    print(f' {magyka.craftItem.get_name()}{" x" + str(magyka.craftRecipe["quantity"] * option) if quantity else ""} added to your inventory!')
                    
                    control.press_enter()
                    return
                else:
                    print(f' {text.lightred} You cannot craft that many.')
                    control.press_enter()
            elif self.code(option):
                return
    
    def market(self):
        while 1:
            self.returnScreen = "town"
            text.clear()
            
            text.header("Flea Market")
            print("")
            
            for i in range((self.page - 1) * 10, min(self.page * 10, len(magyka.player.inventory))):
                if magyka.player.inventory[i][0].type == "equipment":
                    quantity = False
                else:
                    quantity = True
                print(f' {str(i)[:-1]}({str(i)[-1]}) {magyka.player.inventory[i][0].get_name()}{" x" + str(magyka.player.inventory[i][1]) if quantity else ""}')
            
            if len(magyka.player.inventory) == 0:
                print(f' {text.darkgray}Empty{text.reset}')
            
            next = len(magyka.player.inventory) > self.page * 10
            previous = self.page > 1
            
            text.options((["Next"] if next else []) + (["Previous"] if previous else []))
            option = control.get_input("optionumeric", textField=False, options=("n" if next else "")+("p" if previous else "")\
            +"".join(tuple(map(str, range(0, len(magyka.player.inventory))))))
            
            if option in tuple(map(str, range(0, len(magyka.player.inventory) + (self.page-1) * 10 + 1))):
                magyka.sellItem = magyka.player.inventory[int(option) + (self.page - 1) * 10][0]
                self.nextScreen = "sell"
                return
            elif option == "n":
                self.page += 1
            elif option == "p":
                self.page -= 1
            elif self.code(option):
                return
    
    def sell(self):
        while 1:
            self.returnScreen = "market"
            self.nextScreen = self.returnScreen
            text.clear()
            
            text.header("Sell " + magyka.sellItem.name)
            
            magyka.sellItem.show_stats()
            
            print(f'\n {text.gp}{text.reset} {magyka.player.gold}')
            print(f'\n Currently owned: {magyka.player.num_of_items(magyka.sellItem.name)}')
            print(f'\n Sell Value: {text.gp}{text.reset} {round(magyka.sellItem.value * 0.7)}')
            print(f' Type the quantity of items to be sold ({magyka.player.num_of_items(magyka.sellItem.name)} can be sold).')
            
            option = control.get_input("numeric")
            
            print("")
            
            try:
                option = int(option)
            except:
                pass
            
            if type(option) is int:
                if option <= magyka.player.num_of_items(magyka.sellItem.name):
                    sound.play_sound("coin")
                    magyka.player.remove_item(magyka.sellItem, option)
                    magyka.player.gold += round(magyka.sellItem.value * 0.7)
                    
                    if magyka.sellItem.type in Globals.stackableItems:
                        quantity = True
                    else:
                        quantity = False
                    print(f' Sold {magyka.sellItem.get_name()}{" x" + str(option) if quantity else ""}.')
                    
                    control.press_enter()
                    return
                else:
                    if magyka.sellItem.type in Globals.stackableItems:
                        quantity = True
                    else:
                        quantity = False
                    print(f' {text.lightred} You cannot sell that many.')
                    control.press_enter()
                    return
            elif self.code(option):
                return
    
    # - Character
    def character(self):
        while 1:
            self.returnScreen = "camp"
            text.clear()
            Image("background").show_at_origin()
            Image("screen/Character").show_at_description()
            text.header("Character")
            text.move_cursor(1, 1)
            magyka.player.show_stats()
            
            text.options(["Inventory", "Equipment", "Quests", "Stats"])
            option = control.get_input("alphabetic", options="ieqs")
            
            if option == "i":
                self.page = 1
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
            elif self.code(option):
                return
    
    def inventory(self):
        while 1:
            self.returnScreen = "character"
            text.clear()
            Image("background").show_at_origin()
            Image("screen/Inventory").show_at_description()
            text.header("Inventory")
            print("")
            
            for i in range((self.page - 1) * 10, min(self.page * 10, len(magyka.player.inventory))):
                item = magyka.player.inventory[i]
                if i >= 100:
                    just = ""
                elif i >= 10:
                    just = " "
                else:
                    just = "  "
                text.print_at_loc(f'{str(i)[:-1]}({str(i)[-1]}) {just}{item[0].get_name(True, item[1])}', 3 + int(str(i)[-1]), 4)
            
            if len(magyka.player.inventory) == 0:
                text.print_at_loc('{text.darkgray}Empty{text.reset}', 3, 4)
            
            print("")
            
            next = len(magyka.player.inventory) > self.page * 10
            previous = self.page > 1
            
            text.options((["Next"] if next else []) + (["Previous"] if previous else []))
            option = control.get_input("optionumeric", textField=False, options=("n" if next else "")+("p" if previous else "")\
            +"".join(tuple(map(str, range(0, len(magyka.player.inventory))))))
            
            if option in tuple(map(str, range(0, len(magyka.player.inventory) + (self.page-1) * 10 + 1))):
                magyka.inspectItem = magyka.player.inventory[int(option) + (self.page - 1) * 10][0]
                magyka.inspectItemEquipped = False
                self.nextScreen = "inspect"
                return
            elif option == "n":
                self.page += 1
            elif option == "p":
                self.page -= 1
            elif self.code(option):
                return
    
    def equipment(self):
        while 1:
            self.returnScreen = "character"
            text.clear()
            Image("background").show_at_origin()
            Image("screen/Equipment").show_at_description()
            text.header("Equipment")
            print("")
            
            for i in range(len(Globals.slotList)):
                text.print_at_loc(f'{i}) {Globals.slotList[i].capitalize()}', 3 + i, 4)
                if magyka.player.equipment[Globals.slotList[i]]:
                    text.print_at_loc(f'{magyka.player.equipment[Globals.slotList[i]].get_name()}', 3 + i, 14)
                else:
                    text.print_at_loc(f'{text.darkgray}Empty{text.reset}', 3 + i, 14)
            
            option = control.get_input("numeric", options="".join(tuple(map(str, range(0, len(Globals.slotList))))))
            
            if option in tuple(map(str, range(0, len(Globals.slotList)))) and magyka.player.equipment[Globals.slotList[int(option)]] != "":
                magyka.inspectItem = magyka.player.equipment[Globals.slotList[int(option)]]
                magyka.inspectItemEquipped = True
                self.nextScreen = "inspect"
                return
            elif self.code(option):
                return
    
    def inspect(self):
        while 1:
            self.returnScreen = self.oldScreen
            self.nextScreen = self.returnScreen
            text.clear()
            Image("background").show_at_origin()
            Image("item/" + magyka.inspectItem.name).show_at_description()
            
            if magyka.inspectItemEquipped:
                magyka.inspectItem.update()
            magyka.player.update_stats()
            
            text.header("Inspect " + magyka.inspectItem.type.capitalize())
            text.move_cursor(2, 1)
            magyka.inspectItem.show_stats()
            text.slide_cursor(1, 3)
            print(f'Value: {text.gp} {text.reset}{magyka.inspectItem.value}')
            
            if magyka.inspectItem.type == "equipment":
                text.options((["Unequip"] if magyka.inspectItemEquipped else ["Equip", "Discard"])+["More Info"])
                option = control.get_input("alphabetic", options=("u" if magyka.inspectItemEquipped else "ed")+"m", silentOptions=("u" if magyka.inspectItemEquipped else "e"))
            elif magyka.inspectItem.type == "consumable":
                text.options((["Use"] if magyka.inspectItem.target == "self" else [])+["Discard"])
                option = control.get_input("alphabetic", options=("u" if magyka.inspectItem.target == "self" else "")+"d")
            elif magyka.inspectItem.type == "modifier":
                text.options(["Use", "Discard"])
                option = control.get_input("alphabetic", options="ud")
            else:
                text.options(["Discard"])
                option = control.get_input("alphabetic", options="d")
            
            if option == "u" and magyka.inspectItem.type == "equipment":
                sound.play_sound("equip")
                magyka.player.unequip(magyka.inspectItem.slot)
                return
            elif option == "u" and magyka.inspectItem.type == "consumable" and magyka.inspectItem.target == "self":
                print("NEED USEITEM FUNCTION")
                #text, z, y = useItem(item, player)
                #for line in text:
                #    print(evalText(line))
                control.press_enter()
                if magyka.player.num_of_items(magyka.inspectItem.name) <= 0:
                    return
            elif option == "u" and magyka.inspectItem.type == "modifier":
                s_applyModifier(magyka.inspectItem)
                if "infinite" not in magyka.inspectItem.tags: magyka.player.remove_item(magyka.inspectItem)
                if magyka.player.num_of_items(magyka.inspectItem.name) <= 0:
                    return
            elif option == "e" and magyka.inspectItem.type == "equipment":
                sound.play_sound("equip")
                magyka.player.equip(magyka.inspectItem)
                return
            elif option == "d":
                if magyka.player.num_of_items(magyka.inspectItem.name) > 1:
                    while 1:
                        text.clear()
                        text.header("Quantity")
                        print(f'\n Type the quantity to discard (1-{magyka.player.num_of_items(magyka.inspectItem.name)})')

                        option = control.get_input("numeric")

                        if option in tuple(map(str, range(1, magyka.player.num_of_items(magyka.inspectItem.name)+1))):
                            magyka.player.remove_item(magyka.inspectItem, int(option))
                            return
                        elif self.code(option):
                            break
                else:
                    magyka.player.remove_item(magyka.inspectItem)
                    break
            elif self.code(option):
                return
    
    def stats(self):
        while 1:
            self.returnScreen = "character"
            text.clear()
            text.header("Stats")
            
            stats = magyka.player.stats.copy()
            stats.pop("max hp")
            stats.pop("max mp")
            stats.pop("attack")
            
            statNamePad = len(max(magyka.player.stats, key=len)) + 1
            statValuePad = len(max([str(magyka.player.stats[stat]) for stat in stats], key=len))
            
            magyka.player.show_stats(passives=False)
            print("")
            print(f' {"Attack".ljust(statNamePad)}: {(str(magyka.player.stats["attack"][0]) + " - " + str(magyka.player.stats["attack"][1])).ljust(statValuePad)}')
            
            for stat in stats:
                if magyka.player.baseStats[stat] <= magyka.player.stats[stat]:
                    changeString = "+"
                else:
                    changeString = "-"
                print(f' {stat.capitalize().ljust(statNamePad)}: {str(magyka.player.stats[stat]).ljust(statValuePad)} ({changeString}{magyka.player.stats[stat] - magyka.player.baseStats[stat]})')
            
            text.header("Passives")
            
            for i in range((self.page - 1) * 10, min(self.page * 10, len(magyka.player.passives))):
                print(f' {str(i)[:-1]}({str(i)[-1]}) {magyka.player.passives[i].get_name(turns=True)}')
            
            if len(magyka.player.passives) == 0:
                print(f' {text.darkgray}No Passives{text.reset}')
            
            next = len(magyka.player.passives) > self.page * 10
            previous = self.page > 1
            
            text.options((["Next"] if next else []) + (["Previous"] if previous else []))
            option = control.get_input("optionumeric", textField=False, options=("n" if next else "")+("p" if previous else "")\
            +"".join(tuple(map(str, range(0, len(magyka.player.passives))))))
            
            if option in tuple(map(str, range(0, len(magyka.player.passives) + (self.page-1) * 10 + 1))):
                magyka.inspectPassive = magyka.player.passives[int(option) + (self.page - 1) * 10]
                self.nextScreen = "inspect_passive"
                return
            elif option == "n":
                self.page += 1
            elif option == "p":
                self.page -= 1
            elif self.code(option):
                return
    
    def inspect_passive(self):
        while 1:
            self.returnScreen = "stats"
            self.nextScreen = self.returnScreen
            text.clear()
            text.header("Inspect passive")
            print(f'\n Name: {magyka.inspectPassive.get_name(turns=True)}')
            print(f' Description: {magyka.inspectPassive.description}\n')
            
            for effect in magyka.inspectPassive.effect:
                effect.show_stats()
            
            control.get_input("none")
            return
    
    def rest(self):
        self.nextScreen = self.returnScreen
        hp = math.floor(magyka.player.stats["max hp"] * 0.85)
        mp = math.floor(magyka.player.stats["max mp"] * 0.85)
        if magyka.player.hp >= hp and magyka.player.mp >= mp:
            return
        if hp > magyka.player.hp:
            magyka.player.hp = hp
        if mp > magyka.player.mp:
            magyka.player.mp = mp
        sound.play_sound("rest")


if __name__ == "__main__":
    if Globals.system == "Windows":
        import win32api
        win32api.SetConsoleCtrlHandler(exit_handler, True)
    else:
        import signal
        signal.signal(signal.SIGHUP, exit_handler)

    try:
        magyka = Magyka()
        screen = Screen()
    except Exception as err:
        print("")
        traceback.print_exc()
        control.press_enter()
