from script.Control import control
from script.Effect import Effect, Passive
from script.Entity import Entity
import script.Globals as Globals
from script.Image import Image
from script.Item import Item, Enchantment, Modifier
from script.Logger import logger
from script.Loot import Loot
from script.Mapper import mapper
from script.Settings import settings
from script.Sound import sound
from script.Text import text
from script.World import World
import copy
import json
import math
import os
import random
import re
import sqlite3
import sys
import time
import traceback

"""
TODO
replace old code instances
map class
 - text on map
enemy skills
equippable skills
equipped weapon skill
dynamic hp bars based on enemy kill count and knowledge
achievement system
tutorial mode
"""


def dict_factory(cursor, row):
    # Converts sqlite return value into a dictionary with column names as keys
    d = {}
    for i, col in enumerate(cursor.description):
        d[col[0]] = row[i]

    return d


def exit_handler(*args):
    world.save()
    text.set_cursor_visible(True)
    if Globals.system != "Windows":
        control.reset_input_settings()


class Manager:
    """
    Holds runtime data and handles interactions needing multiple classes.
    """

    def __init__(self):
        """
        Initializes the class, loads data files, and generates saves.
        """

        text.clear()

        self.session = sqlite3.connect("data/data.db")
        self.session.row_factory = dict_factory
        self.cur = self.session.cursor()

        self.nextScreen = ""
        self.inspectItem = None
        self.inspectSlot = ""
        self.purchaseItem = None
        self.craftItem = None
        self.craftRecipe = None
        self.sellItem = None
        self.inspectPassive = None
        self.itemLog = None
        self.hunt = False
        self.encounterSteps = 10
        self.encounterStepCounter = 0

        self.world = World({})
        self.saves = []

        for file in os.listdir("saves"):
            if file.endswith(".json"):
                try:
                    with open("saves/" + file, "r") as saveFile:
                        self.saves.append(json.loads(saveFile.read()))
                except:
                    self.saves.append(file.split(".")[0])
                    logger.log(f'Error loading world file:\n\n{traceback.format_exc()}')

        for i in range(len(self.saves)-1, -1, -1):
            if type(self.saves[i]) is str:
                try:
                    with open("saves/" + self.saves[i] + " backup.json", "r") as saveFile:
                        self.saves[i] = json.loads(saveFile.read())
                except:
                    self.saves.pop(i)
                    logger.log(f'Error loading backup world file:\n\n{traceback.format_exc()}')

    def init_world(self):
        with open("data/portals.json") as portalFile:
            mapPortals = json.load(portalFile)

        with open("data/encounters.json", "r") as encounterFile:
            encounters = json.load(encounterFile)

        with open("data/stores.json", "r") as storeFile:
            stores = json.load(storeFile)

        with open("data/quests.json", "r") as questFile:
            quests = json.load(questFile)

        recipes = self.cur.execute('select * from recipes').fetchall()

        for i in range(len(recipes)):
            recipes[i]["ingredients"] = json.loads(recipes[i]["ingredients"])
        
        self.world.__init__({
            "maps": {},
            "encounters": encounters,
            "stores": stores,
            "quests": quests,
            "recipes": recipes
        })

    def load_world(self, save):
        self.world = World(save)

        if self.world.attributes["player"]:
            self.world.attributes["player"] = self.load("enemies", self.world.attributes["player"])
        if self.world.attributes["enemy"]:
            self.world.attributes["enemy"] = self.load("enemies", self.world.attributes["enemy"])

    def load(self, table, obj):
        """
        Formats an object from a python dict to Magyka classes.

        Args:
            table:
                String database table of the item.

                "effects", "passives", "enchantments", "lootTables", "items".
            obj:
                Dict datatable row.

        Returns:
            Magyka class.
        """

        try:
            if table == "effects":
                if "passive" in obj:
                    for i in range(len(obj["passive"])):
                        if type(obj["passive"][i]) is str:
                            obj["passive"][i] = self.load_from_db("passives", obj["passive"][i])
                        else:
                            obj["passive"][i] = self.load("passives", obj["passive"][i])
            elif table == "passives":
                pass
            elif table == "enchantments":
                obj.update({"level": 1, "tier": 0, "baseName": obj["name"]})
            elif table == "modifiers":
                pass
            elif table == "lootTables":
                for i in range(len(obj["drops"])):
                    if type(obj["drops"]) is list:
                        for j in range(len(obj["drops"][i][0])):
                            obj["drops"][i][0][j] = self.load_from_db("items", obj["drops"][i][0][j])
                    else:
                        obj["drops"][i][0] = self.load_from_db("items", obj["drops"][i][0])
            elif table == "items":
                for i in range(len(obj["enchantments"])):
                    if type(obj["enchantments"][i]) is str:
                        obj["enchantments"][i] = self.load("enchantments", obj["enchantments"][i])
                    else:
                        level, tier = obj["enchantments"][i][1], obj["enchantments"][i][2]
                        obj["enchantments"][i] = self.load_from_db("enchantments", obj["enchantments"][i][0])
                        obj["enchantments"][i].update(level, tier)

                if "loot" in obj["tags"]:
                    if type(obj["tags"]["loot"]) is str:
                        obj["tags"]["loot"] = self.load_from_db("lootTables", obj["tags"]["loot"])
                    else:
                        obj["tags"]["loot"] = self.load("lootTables", obj["tags"]["loot"])

                if obj["type"] == "equipment":
                    obj.update({"modifier": self.load_from_db("modifiers", "Normal")})
            elif table == "enemies":
                for i in range(len(obj["inventory"])):
                    obj["inventory"][i][0] = self.load("items", obj["inventory"][i][0])
                for i in range(len(obj["passives"])):
                    obj["passives"][i] = self.load("passives", obj["passives"][i])
                for slot in obj["equipment"]:
                    if obj["equipment"][slot]:
                        obj["equipment"][slot] = self.load("items", obj["equipment"][slot])

            if "effect" in obj:
                for i in range(len(obj["effect"])):
                    obj["effect"][i] = self.load("effects", obj["effect"][i])

            if obj.get("tags"):
                if "passive" in obj["tags"]:
                    for i in range(len(obj["tags"]["passive"])):
                        if type(obj["tags"]["passive"][i]) is str:
                            if table == "enchantments":
                                obj["tags"]["passive"][i] = [self.load_from_db("passives", obj["tags"]["passive"][i])]
                            else:
                                obj["tags"]["passive"][i] = self.load_from_db("passives", obj["tags"]["passive"][i])
                        else:
                            obj["tags"]["passive"][i] = self.load("passives", obj["tags"]["passive"][i])

            if table == "effects":
                obj = Effect(obj)
            elif table == "passives":
                obj = Passive(obj)
            elif table == "enchantments":
                obj = Enchantment(obj)
            elif table == "modifiers":
                obj = Modifier(obj)
            elif table == "lootTables":
                obj = Loot(obj)
            elif table == "items":
                obj = Item(obj)
            elif table == "enemies":
                obj = Entity(obj)
        except:
            logger.log(f'{obj}\n\n{traceback.format_exc()}')
            obj = None

        return obj

    def load_from_db(self, table, name):
        # Select item from DB
        obj = self.cur.execute('select * from ' + table + ' where name="' + name + '"').fetchone()

        # Return if no item found
        if not obj:
            logger.log(f'"{table}.{name}" could not be found.')
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
                logger.log(
                    f'"{jsonLoad}" could not be read from "{table}.{name}".'
                    f'\nPassed value was "{obj[jsonLoad]}".'
                )

        return self.load(table, obj)

    def dev_command(self, command):
        commandSplit = command.split(" ", 1)

        # Zero argument Command Handling
        if command == "s":
            self.world.attributes["player"].attributes["name"] = "Vincent"
            self.world.attributes["player"].attributes["saveId"] = 69420

            self.world.attributes["player"].attributes["extraStats"].update({
                "hpPerLevel": 3,
                "mpPerLevel": 1,
                "strengthPerLevel": 2,
                "vitalityPerLevel": 1,
                "intelligencePerLevel": 0
            })
            self.world.attributes["player"].attributes["baseStats"].update({
                "hit": 95,
                "dodge": 5
            })

            self.world.attributes["player"].attributes["class"] = "Developer"
            self.world.attributes["player"].update_stats()

            self.nextScreen = "camp"
            return True
        elif command == "qs":
            self.world.attributes["player"].attributes["name"] = "Dev"
            self.world.attributes["player"].attributes["saveId"] = 69420
            self.world.attributes["player"].attributes["gold"] = 999999999
            self.dev_command("give all")

            self.world.attributes["player"].attributes["extraStats"].update({
                "hpPerLevel": 3,
                "mpPerLevel": 1,
                "strengthPerLevel": 2,
                "vitalityPerLevel": 1,
                "intelligencePerLevel": 0
            })

            self.world.attributes["player"].attributes["baseStats"].update({
                "hit": 95,
                "dodge": 5
            })

            self.world.attributes["player"].attributes["class"] = "Developer"
            self.world.attributes["player"].update_stats()

            self.nextScreen = "camp"
            return True
        elif command == "restart":
            text.clear()
            os.execv(sys.executable, ['python'] + sys.argv)
        elif command == "heal":
            self.world.attributes["player"].attributes["hp"] = self.world.attributes["player"].attributes["stats"]["max hp"]
            self.world.attributes["player"].attributes["mp"] = self.world.attributes["player"].attributes["stats"]["max mp"]
        elif command == "buy":
            self.world.attributes["player"].add_item(self.purchaseItem)
        elif command == "kill":
            self.battleEnemy.attributes["hp"] = 0
            self.nextScreen = "victory"
            return True
        elif command == "level":
            self.world.attributes["player"].attributes["xp"] = self.world.attributes["player"].attributes["mxp"]
            self.world.attributes["player"].level_up()
        elif command == "god":
            settings.godMode = not settings.godMode
            text.slide_cursor(1, 3)
            print(f'Godmode set to {settings.godMode}')
            control.press_enter()

        # Single Argument Command Handling
        elif commandSplit[0] == "exec":
            try:
                exec(commandSplit[1])
            except:
                text.clear()
                traceback.print_exc()
                logger.log(traceback.format_exc())
                control.press_enter()
        elif commandSplit[0] == "execp":
            try:
                text.slide_cursor(1, 3)
                print(str(eval(commandSplit[1])))
                control.press_enter()
            except:
                text.clear()
                traceback.print_exc()
                logger.log(traceback.format_exc())
                control.press_enter()
        elif commandSplit[0] == "clear":
            if commandSplit[1] == "inventory":
                self.world.attributes["player"].attributes["inventory"] = []
            elif commandSplit[1] == "equipment":
                for slot in self.world.attributes["player"].attributes["equipment"]:
                    self.world.attributes["player"].attributes["equipment"][slot] = ""
                self.world.attributes["player"].update_stats()
            elif commandSplit[1] == "passives":
                self.world.attributes["player"].attributes["passives"] = []
                self.world.attributes["player"].update_stats()
        elif commandSplit[0] == "give":
            commandSplitComma = commandSplit[1].split(", ")
            try:
                if commandSplitComma[0] == "all":
                    devItems = [item["name"] for item in manager.session.cursor().execute("select * from items").fetchall()]
                    for item in devItems:
                        self.world.attributes["player"].add_item(self.load_from_db("items", item))
                else:
                    quantity = 1 if len(commandSplitComma) == 1 else commandSplitComma[1]
                    self.world.attributes["player"].add_item(self.load_from_db("items", commandSplitComma[0]), quantity)
            except:
                traceback.print_exc()
                control.press_enter()
        elif commandSplit[0] == "equip":
            try:
                item = self.load_from_db("items", commandSplit[1])
                self.world.attributes["player"].equip(item)
                text.slide_cursor(1, 3)

                if item:
                    print(f'Equipped {item.get_name()}')
                else:
                    print(f'Failed to equip "{commandSplit[1]}"')

                control.press_enter()
            except Exception:
                traceback.print_exc()
                control.press_enter()
        elif commandSplit[0] == "enchant":
            commandSplitComma = commandSplit[1].split(", ")
            try:
                enchantment = self.load_from_db("enchantments", commandSplitComma[0])
                enchantment.attributes["tier"] = commandSplitComma[1]
                enchantment.attributes["level"] = commandSplitComma[2]
                self.inspectItem.enchant(enchantment)
            except Exception:
                traceback.print_exc()
                control.press_enter()
        elif commandSplit[0] == "passive":
            passive = self.load_from_db("passives", commandSplit[1])
            self.world.attributes["player"].add_passive(passive)
        elif commandSplit[0] == "fight":
            self.battleEnemy = self.load_from_db("enemies", commandSplit[1])
            self.nextScreen = "battle"
            return True

        # Multiple Command Argument Handling
        elif commandSplit[0] == "player":
            commandSplitComma = commandSplit[1].split(", ")
            world.attributes["player"].attributes[commandSplitComma[0]] = int(commandSplitComma[1])
        elif commandSplit[0] == "stats":
            commandSplitComma = commandSplit[1].split(", ")
            world.attributes["player"].attributes["stats"][commandSplitComma[0]] = int(commandSplitComma[1])
        elif commandSplit[0] == "baseStats":
            commandSplitComma = commandSplit[1].split(", ")
            world.attributes["player"].attributes["baseStats"][commandSplitComma[0]] = int(commandSplitComma[1])
            world.attributes["player"].update_stats()
        elif command != "" and command != "/C":
            print("\n That's not a command, stupid.")
            control.press_enter()

        return False

    @staticmethod
    def react_flash(timeout):
        """
        Flashes the screen then waits for input for a specified length of time.

        Args:
            timeout:
                Integer timeout in milliseconds.

        Returns:
            Integer reaction time in milliseconds.
        """

        time.sleep(0.1)
        text.clear()
        Image("red").show_at_origin()
        return control.time_keypress(timeout)

    def load_encounter(self, level=1):
        """
        Loads an enemy and sets it to the correct level.

        Args:
            level:
                Integer level of the enemy.
        """

        enemies = copy.deepcopy(self.encounters[self.world.attributes["player"].location])
        weight = 0
        minLevel = level
        maxLevel = level + 5

        if self.world.attributes["player"].attributes["level"] >= maxLevel - 1:
            minLevel = maxLevel - 1
        if self.world.attributes["player"].attributes["level"] == 1 and level == 1:
            minLevel = 1
            maxLevel = 2
        elif self.world.attributes["player"].attributes["level"] == 2 and level <= 2:
            minLevel = 1
            maxLevel = 2
        level = random.randint(minLevel, maxLevel)

        for i in range(len(enemies)-1, -1, -1):
            enemy = enemies[i][1] = self.load_from_db("enemies", enemies[i][1])
            if level < enemy.attributes["level"][0]\
                    or enemy.attributes["level"][0] > maxLevel\
                    or enemy.attributes["level"][1] < level:
                enemies.pop(i)
                continue

            if level - enemy.attributes["level"][0] > 0:
                enemy.levelDifference = level - enemy.attributes["level"][0]

            enemy.attributes["level"] = level

            enemies[i][0] *= 10
            if enemy.attributes["level"] - minLevel > 0:
                enemies[i][0] -= (enemy.attributes["level"] - minLevel) * 100
            if enemies[i][0] <= 0:
                enemies[i][0] = 1

            for stat in enemy.attributes["baseStats"]:
                if stat in ("strength", "vitality", "intelligence", "crit", "hit", "dodge"):
                    enemy.attributes["baseStats"][stat] += round(0.5 * enemy.attributes["levelDifference"])
                elif stat in ("max hp", "max mp"):
                    enemy.attributes["baseStats"][stat] += round(
                        max(enemy.attributes["baseStats"][stat] * 0.1, 1)
                    ) * enemy.attributes["levelDifference"]

            enemy.update_stats()
            enemies[i][0] += weight
            weight += enemies[i][0] - weight

        enemies = dict(enemies[::-1])

        try:
            weightNum = random.randint(1, weight)
        except:
            self.battleEnemy = None
            return

        for weight, enemy in enemies.items():
            if weight > weightNum:
                self.battleEnemy = enemy
                break


class Screen:
    """
    Handles menus and visuals shown to player. Contains actual "game" code.
    """

    def __init__(self):
        """
        Initializes the class and starts the game loop.
        """

        self.nextScreen = "title_screen"
        self.lastScreen = ""
        self.returnScreen = ""
        self.oldScreen = ""
        self.storeType = ""
        self.page = 1
        self.saveBackup = False

        manager.inspectItemEquipped = False

        while 1:
            if self.nextScreen == "camp" and world.attributes["player"].attributes["class"] != "Developer":
                self.saveBackup = True
            if self.saveBackup:
                world.save(backup=True)
            if manager.nextScreen:
                self.nextScreen = manager.nextScreen
                manager.nextScreen = ""

            try:
                if self.oldScreen != self.lastScreen:
                    self.oldScreen = self.lastScreen
                next_screen = getattr(self, self.nextScreen)
                self.lastScreen = self.nextScreen
            except AttributeError:
                logger.log(f'Screen "{self.nextScreen}" does not exist (from screen "{self.lastScreen}").')
                next_screen = getattr(self, self.lastScreen)
            next_screen()

    def code(self, option):
        """
        Detects and returns a back Bool if a code is detected.

        Args:
            option:
                String option.

        Returns:
            Boolean
        """

        if option == "/B":
            self.nextScreen = self.returnScreen
            text.set_cursor_visible(False)
            return True
        elif option == "/D":
            command = control.get_input("command")
            return manager.dev_command(command)
        elif option == "/C":
            text.clear()
            text.set_cursor_visible(False)
            return False

        return False

    # - Main Menu
    def title_screen(self):
        while 1:
            self.returnScreen = "title_screen"
            text.clear()

            print("\n ", end="")
            print("Welcome to the world of...\n")

            title = open("text/magyka title.txt", "r").read().split("\n")
            for i in range(len(title)):
                print(text.cc([
                    "026", "012", "006", "039",
                    "045", "019", "020", "021",
                    "004", "027", "026", "012",
                    "006", "039", "000", "039",
                    "006", "012"
                ][i]) + title[i] + text.reset)

            options = text.options(
                ["New Game"] +
                (["Continue"] if len(manager.saves) > 0 else [text.darkgray + "Continue"]) +
                ["Load Game"]
            )
            option = control.get_input(options=options, back=False)

            if option == "n":
                self.nextScreen = "new_game"
                return
            elif option == "c":
                manager.load_world(manager.saves[0])
                self.nextScreen = "camp"
                return
            elif option == "l":
                self.nextScreen = "load_game"
                return
            elif self.code(option):
                return

    def new_game(self):
        self.returnScreen = "title_screen"
        select = 1
        while 1:
            if select == 1:
                while 1:
                    text.clear()
                    text.background()
                    text.header("World Creation")
                    text.move_cursor(3, 4)
                    print("World Name")

                    option = control.get_input("alphanumeric")

                    if not 1 < len(option) < 22:
                        text.slide_cursor(1, 3)
                        print("Your name must be between 2 and 14 characters.")
                        control.press_enter()
                        continue
                    elif re.match(r"\w\s", option):
                        text.slide_cursor(1, 3)
                        print("Your name contains illegal characters.")
                        control.press_enter()
                        continue
                    elif self.code(option):
                        return

                    world.attributes["name"] = option.title()
                    select += 1
                    break
            elif select == 2:
                while 1:
                    text.clear()
                    text.background()
                    text.header("World Creation")
                    text.move_cursor(3, 4)
                    print("Difficulty (these don't do anything yet just choose one lmao)")

                    options = text.options(["Coward", "Average", "Gamer", "Masochist"])
                    option = control.get_input(options=options)

                    if option in options:
                        select += 1
                        break
                    elif self.code(option):
                        select -= 1
                        break
            elif select == 3:
                while 1:
                    text.clear()
                    text.background()
                    text.header("Character Creation")
                    text.move_cursor(3, 4)
                    print("Player Name")

                    option = control.get_input("alphanumeric")

                    if not 1 < len(option) < 22:
                        text.slide_cursor(1, 3)
                        print("Your name must be between 2 and 14 characters.")
                        control.press_enter()
                        continue
                    elif re.match(r"\w\s", option):
                        text.slide_cursor(1, 3)
                        print("Your name contains illegal characters.")
                        control.press_enter()
                        continue
                    elif self.code(option):
                        return

                    world.attributes["player"].attributes["name"] = option.title()
                    select += 1
                    break
            elif select == 4:
                while 1:
                    self.nextScreen = "camp"
                    text.clear()
                    text.background()
                    text.header("Class")

                    classes = {
                        "i": "Infantryman",
                        "w": "Warrior",
                        "k": "Knight",
                        "s": "Spellsword",
                        "m": "Magye"
                    }

                    text.move_cursor(2, 4)
                    options = text.options(list(classes.values()))
                    option = control.get_input(options=options)

                    playerClass = ""

                    if option in options:
                        playerClass = classes[option]
                    elif self.code(option):
                        select -= 1
                        break

                    text.clear()
                    text.background()
                    text.print_at_description(open("text/" + playerClass + ".txt").readlines())
                    text.move_cursor(3, 4)
                    print(f'Are you sure you wish to choose {playerClass}? There is no going back.')

                    options = text.options(["Yes", "No"])
                    option = control.get_input(options=options)

                    if option == "n":
                        continue
                    elif option == "y":
                        pass
                    elif self.code(option):
                        select -= 1
                        break

                    if playerClass == "Infantryman":
                        world.attributes["player"].attributes["extraStats"].update({
                            "hpPerLevel": 3,
                            "mpPerLevel": 1,
                            "strengthPerLevel": 2,
                            "vitalityPerLevel": 2,
                            "intelligencePerLevel": 0
                        })
                        world.attributes["player"].attributes["baseStats"].update({
                            "hit": 95,
                            "dodge": 6,
                            "crit": 5
                        })
                    elif playerClass == "Warrior":
                        world.attributes["player"].attributes["extraStats"].update({
                            "hpPerLevel": 3,
                            "mpPerLevel": 1,
                            "strengthPerLevel": 2,
                            "vitalityPerLevel": 1,
                            "intelligencePerLevel": 0
                        })
                        world.attributes["player"].attributes["baseStats"].update({
                            "hit": 95,
                            "dodge": 5
                        })
                    elif playerClass == "Knight":
                        world.attributes["player"].attributes["extraStats"].update({
                            "hpPerLevel": 4,
                            "mpPerLevel": 1,
                            "strengthPerLevel": 2,
                            "vitalityPerLevel": 2,
                            "intelligencePerLevel": 0
                        })
                        world.attributes["player"].attributes["baseStats"].update({
                            "hit": 85,
                            "dodge": 1,
                            "crit": 2
                        })
                    elif playerClass == "Spellsword":
                        world.attributes["player"].attributes["extraStats"].update({
                            "hpPerLevel": 2,
                            "mpPerLevel": 2,
                            "strengthPerLevel": 1,
                            "vitalityPerLevel": 1,
                            "intelligencePerLevel": 1
                        })
                        world.attributes["player"].attributes["baseStats"].update({
                            "hit": 92
                        })
                    elif playerClass == "Magye":
                        world.attributes["player"].attributes["extraStats"].update({
                            "hpPerLevel": 2,
                            "mpPerLevel": 3,
                            "strengthPerLevel": 0,
                            "vitalityPerLevel": 0,
                            "intelligencePerLevel": 3
                        })
                        world.attributes["player"].attributes["baseStats"].update({
                            "dodge": 4,
                            "crit": 3
                        })

                    world.attributes["player"].attributes["class"] = playerClass
                    world.attributes["player"].update_stats()

                    self.nextScreen = "camp"
                    if Globals.system == "Windows":
                        win32api.SetConsoleCtrlHandler(exit_handler, True)
                    else:
                        signal.signal(signal.SIGHUP, exit_handler)

                    manager.init_world()
                    return

    def load_game(self):
        while 1:
            self.returnScreen = "title_screen"
            text.clear()
            text.background()
            Image("screen/continue").show_at_description()
            text.header("Continue")

            for i in range(len(manager.saves)):
                text.move_cursor(3 + i, 4)
                save = (
                    manager.saves[i]["name"] +
                    text.title(
                        manager.saves[i]["attributes"]["player"]["name"],
                        manager.saves[i]["attributes"]["player"]["level"],
                        manager.saves[i]["attributes"]["player"]["playerClass"]
                    )
                )
                print(f'({i}) {save}')

            if len(manager.saves) == 0:
                text.move_cursor(3, 4)
                print(f'{text.darkgray}Empty{text.reset}')

            print("")
            options = text.options(["Delete"])
            option = control.get_input(
                "optionumeric",
                options=options+"".join(tuple(map(str, range(0, len(manager.saves)))))
            )

            if option in tuple(map(str, range(0, len(manager.saves)))):
                manager.load_world(manager.saves[int(option)])
                self.nextScreen = "camp"
                self.returnScreen = "camp"

                if Globals.system == "Windows":
                    win32api.SetConsoleCtrlHandler(exit_handler, True)
                else:
                    signal.signal(signal.SIGHUP, exit_handler)

                return
            elif option == "d":
                self.nextScreen = "delete_save"
                return
            elif self.code(option):
                return

    def delete_save(self):
        while 1:
            self.returnScreen = "load_game"
            text.clear()
            text.background()
            Image("screen/continue").show_at_description()
            text.header("Delete")

            for i in range(len(manager.saves)):
                text.move_cursor(3 + i, 4)
                save = (
                        manager.saves[i]["name"] +
                        text.title(
                            manager.saves[i]["attributes"]["player"]["name"],
                            manager.saves[i]["attributes"]["player"]["level"],
                            manager.saves[i]["attributes"]["player"]["playerClass"]
                        )
                )
                print(f'({i}) {save}')

            if len(manager.saves) == 0:
                text.move_cursor(3, 4)
                print(f'{text.darkgray}Empty{text.reset}')

            option = control.get_input("numeric", options="".join(tuple(map(str, range(0, len(manager.saves))))))

            if option in tuple(map(str, range(0, len(manager.saves)))):
                save = manager.saves[int(option)]
                os.remove("saves/" + save["name"] + str(save["saveId"]) + ".json")
                os.remove("saves/" + save["name"] + str(save["saveId"]) + " backup.json")
                manager.saves.pop(int(option))
                return
            elif self.code(option):
                return

    # - Camp
    def camp(self):
        while 1:
            self.returnScreen = "camp"
            text.clear()
            text.background()
            Image("screen/camp").show_at_description()
            text.header("Camp")
            text.move_cursor(1, 1)
            world.attributes["player"].show_stats()

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
        manager.itemLog = []
        if type(world.attributes["enemy"].level) is list:
            world.attributes["enemy"].level = world.attributes["enemy"].level[0]
        world.attributes["enemy"].hp = world.attributes["enemy"].stats["max hp"]
        world.attributes["enemy"].mp = world.attributes["enemy"].stats["max mp"]

        text.clear()
        text.background()

        def print_player():
            text.print_at_loc(text.title(world.attributes["player"].name, world.attributes["player"].level, world.attributes["player"].playerClass) + " ", 3, 4)
            text.print_at_loc(text.bar(world.attributes["player"].hp, world.attributes["player"].stats["max hp"], "red", length=40, number=True) + " ", 4, 5)
            text.print_at_loc(text.bar(world.attributes["player"].mp, world.attributes["player"].stats["max mp"], "blue", length=40, number=True) + " ", 5, 5)

        def print_enemy():
            text.clear_description()
            text.print_at_loc(text.title(world.attributes["enemy"].name, world.attributes["enemy"].level), 3, 84)
            Image("enemy/" + world.attributes["enemy"].name).show_at_description()

            text.print_at_loc(text.bar(world.attributes["enemy"].hp, world.attributes["enemy"].stats["max hp"], "red") + " ", 24, 85)
            text.print_at_loc(f' {world.attributes["enemy"].hp}/{world.attributes["enemy"].stats["max hp"]}' + " ", 25, 85)
            text.print_at_loc(text.bar(world.attributes["enemy"].mp, world.attributes["enemy"].stats["max mp"], "blue") + " ", 27, 85)
            text.print_at_loc(f' {world.attributes["enemy"].mp}/{world.attributes["enemy"].stats["max mp"]}' + " ", 28, 85)

        print_player()
        print_enemy()

        while 1:
            while 1:
                usedItem = False
                world.attributes["player"].guard = ""
                over = False

                magic = world.attributes["player"].equipment.get("tome") and world.attributes["player"].mp >= world.attributes["player"].equipment["tome"].mana

                text.clear_main()
                print_player()
                print("")

                text.options([(text.darkgray if not magic else "") + "Magic", "Attack", "Guard", "Item", "Cede"])
                option = control.get_input("alphabetic", options="agic" + ("m" if magic else ""), silentOptions="amgc", back=False, showText=False)

                if option in "agic" + ("m" if magic else ""):
                    text.clear_main()
                    print_player()
                    print("")

                if option == "a":
                    sound.play_sound(["attack", "slash"])
                    world.attributes["player"].attack(world.attributes["enemy"])
                    break
                elif option == "m":
                    world.attributes["player"].mp -= world.attributes["player"].equipment["tome"].mana
                    if world.attributes["player"].equipment["tome"].target == "self":
                        world.attributes["player"].attack(world.attributes["player"], type="magic")
                    else:
                        world.attributes["player"].attack(world.attributes["enemy"], type="magic")
                    break
                elif option == "g":
                    guardState = random.randint(1, 5)
                    if settings.alwaysCounter:
                        guardState = 5
                    if guardState <= 3:
                        world.attributes["player"].guard = "deflect"
                    elif guardState == 4:
                        world.attributes["player"].guard = "block"
                    else:
                        world.attributes["player"].guard = "counter"
                    text.slide_cursor(1, 3)
                    print(f'{world.attributes["player"].name} lowers into a defensive stance.')
                    break
                elif option == "i":
                    self.page = 1
                    usedItem = False
                    while 1:
                        text.clear()
                        text.background()
                        Image("screen/Inventory").show_at_description()
                        text.header("Inventory")
                        print("")

                        itemList = []
                        for item in world.attributes["player"].inventory:
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
                        option = control.get_input("optionumeric", options=("n" if next else "")+("p" if previous else "")\
                        +"".join(tuple(map(str, range(0, len(itemList))))))

                        if option in tuple(map(str, range(0, len(itemList) + (self.page-1) * 10 + 1))):
                            item = itemList[int(option) + (self.page - 1) * 10][0]
                            while 1:
                                text.clear()
                                text.background()
                                Image("item/" + item.name).show_at_description()
                                text.header("Use Item")

                                text.move_cursor(2, 1)
                                item.show_stats()

                                text.options(["Use"])
                                option = control.get_input("alphabetic", options="u", silentOptions="u")

                                if option == "u":
                                    usedItem = True

                                    text.clear()
                                    text.background()
                                    print_enemy()
                                    print_player()
                                    print("")

                                    if item.target == "self":
                                        item.use(world.attributes["player"], world.attributes["player"])
                                    else:
                                        item.use(world.attributes["player"], world.attributes["enemy"])

                                    if not item.tags.get("infinite"):
                                        world.attributes["player"].remove_item(item)

                                    itemFound = False
                                    for i in manager.itemLog:
                                        if i[0].name == item.name:
                                            i[1] += 1
                                            itemFound = True
                                            break
                                    if not itemFound:
                                        manager.itemLog.append([item, 1])

                                    break
                                elif self.code(option):
                                    break
                            break
                        elif option == "n":
                            self.page += 1
                        elif option == "p":
                            self.page -= 1
                        elif self.code(option):
                            print_enemy()
                            break
                    if usedItem:
                        break
                elif option == "c":
                    pass # FLEEING
                elif self.code(option):
                    return

            world.attributes["player"].update()
            print_player()
            print_enemy()
            control.press_enter()

            if world.attributes["enemy"].hp <= 0:
                self.nextScreen = "victory"
                return
            elif world.attributes["player"].hp <= 0:
                self.nextScreen = "defeat"
                return

            text.clear_main()
            print_player()
            print("")

            if world.attributes["player"].guard == "counter":
                text.slide_cursor(1, 3)
                print(f'{world.attributes["enemy"].name} {world.attributes["enemy"].text} {world.attributes["player"].name}, but {world.attributes["player"].name} counters, ', end="")
                sound.play_sound(["attack", "slash"])
                world.attributes["player"].attack(world.attributes["enemy"], message=False)
            else:
                sound.play_sound(["hit", "hit2"])
                if settings.godMode:
                    print(f'{world.attributes["player"].name} does not take damage.')
                else:
                    world.attributes["enemy"].attack(world.attributes["player"])

            world.attributes["enemy"].update()
            print_player()
            print_enemy()
            control.press_enter()

            if world.attributes["enemy"].hp <= 0:
                self.nextScreen = "victory"
                return
            elif world.attributes["player"].hp <= 0:
                self.nextScreen = "defeat"
                return

    def victory(self):
        text.clear()
        text.background()
        Image("enemy/"+world.attributes["enemy"].name).show_at_description()
        text.header("Victory")
        sound.play_sound("victory")
        # UPDATE PLAYER QUESTS

        levelDifference = world.attributes["enemy"].level - world.attributes["player"].level

        if levelDifference == 0:
            lootModifier = 1
        else:
            lootModifier = max(round(1.15 ** levelDifference, 2), 0.25)

        xp = math.ceil(world.attributes["enemy"].xp * lootModifier)
        gold = math.ceil(random.randint(math.ceil(world.attributes["enemy"].gold*0.9), math.ceil(world.attributes["enemy"].gold*1.1)) * lootModifier)
        items = manager.load_from_db("lootTables", world.attributes["enemy"].name)
        if items:
            items = items.use()
        else:
            items = []

        world.attributes["player"].gold += gold
        world.attributes["player"].xp += xp
        world.attributes["player"].level_up()

        text.print_at_loc(f'Obtained: (x{lootModifier} Loot Modifier)', 3, 4)
        for i in range(len(items)):
            text.print_at_loc(f'- {items[i][0].get_name(info=True, quantity=items[i][1])}', 4 + i, 5)
            world.attributes["player"].add_item(items[i][0], items[i][1])

        print("")
        text.slide_cursor(0, 4)
        print(f'- {text.gp}{text.reset} {gold}')
        text.slide_cursor(0, 4)
        print(f'- {text.xp}{text.reset} {xp}')

        print("")
        if manager.itemLog:
            text.slide_cursor(0, 3)
            print("Items used:")
            for item in manager.itemLog:
                text.slide_cursor(0, 4)
                print(f'- {item[0].get_name().ljust(28)} x{item[1]}')
        else:
            text.slide_cursor(0, 3)
            print(f'Items used: {text.darkgray}None{text.reset}')
        # SHOW COMPLETED QUESTS

        time.sleep(1)
        control.press_enter()
        self.nextScreen = "map"

    def defeat(self):
        text.clear()
        text.header("Defeat")
        text.background()
        Image("enemy/"+world.attributes["enemy"].name).show_at_description()
        sound.play_sound("defeat")
        text.move_cursor(3, 4)
        print("Defeated by:")
        print("")
        world.attributes["enemy"].show_stats(gpxp=False)

        print("")
        if manager.itemLog:
            text.slide_cursor(0, 3)
            print("Items used:")
            for item in manager.itemLog:
                text.slide_cursor(0, 4)
                print(f'- {item[0].get_name().ljust(28)} x{item[1]}')
        else:
            text.slide_cursor(0, 3)
            print(f'Items used: {text.darkgray}None{text.reset}')

        manager.itemLog = []
        text.slide_cursor(1, 3)
        print(f'You died, ', end="")
        world.attributes["player"].add_passive(manager.load_from_db("passives", "Charon's Curse"))
        world.attributes["player"].hp = 1
        world.attributes["player"].mp = 0

        time.sleep(1)
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
            if world.mapPortals.get(mapName):
                for p in world.mapPortals[mapName]:
                    if p[0] == world.attributes["player"].x and p[1] == world.attributes["player"].y:
                        portal = p

            top = world.attributes["player"].y - mapHeight // 2
            bottom = world.attributes["player"].y + mapHeight // 2
            left = world.attributes["player"].x - mapWidth // 2
            right = world.attributes["player"].x + mapWidth // 2

            if top < 0:
                top = 0
            if bottom > len(mapTiles):
                bottom = len(mapTiles)
            if left < 0:
                left = 0
            if right > len(mapTiles[0]):
                right = len(mapTiles[0])

            text.clear_main_small()
            text.move_cursor(1, 1)
            world.attributes["player"].show_stats(small=True)
            text.slide_cursor(1, 3)
            print(f'{text.reset}Use {settings.moveBind.upper()} to move.')
            text.options(["Hunt"] + ((["Enter"] if settings.interactBind == "e" else ["Approach"]) if portal else []))
            text.slide_cursor(1, 3)

            print(f'Hunting: {"True" if manager.hunt else "False"}')

            for y in range(top, bottom):
                text.move_cursor(mapTop + y - top, mapLeft)
                for x in range(left, right):
                    tile = mapTiles[y][x]

                    if x == world.attributes["player"].x and y == world.attributes["player"].y:
                        print(text.reset + "<>", end="")
                        if x != right:
                            print(text.rgb(mapTiles[y][x + 1], back=True), end="")
                        continue

                    if x > left and tile == mapTiles[y][x - 1]:
                        tileText = "  "
                    else:
                        tileText = text.rgb(tile, back=True) + "  "

                    print(tileText, end="")

            option = control.get_input("alphabetic", options=settings.moveBind+"h"+(settings.interactBind if portal else ""), silentOptions=settings.moveBind, showText=False)

            moveX = 0
            moveY = 0

            if option == settings.moveBind[0] and mapCollision[world.attributes["player"].y-1][world.attributes["player"].x] != "0;0;0":
                moveY -= 1
            elif option == settings.moveBind[1] and mapCollision[world.attributes["player"].y][world.attributes["player"].x-1] != "0;0;0":
                moveX -= 1
            elif option == settings.moveBind[2] and mapCollision[world.attributes["player"].y+1][world.attributes["player"].x] != "0;0;0":
                moveY += 1
            elif option == settings.moveBind[3] and mapCollision[world.attributes["player"].y][world.attributes["player"].x+1] != "0;0;0":
                moveX += 1

            if moveX or moveY:
                world.attributes["player"].x += moveX
                world.attributes["player"].y += moveY

                if manager.hunt:
                    manager.encounterStepCounter += 1
                else:
                    if not settings.encounters and random.randint(1, 20) == 1:
                        manager.encounterStepCounter += 1

                if manager.encounterStepCounter >= manager.encounterSteps:
                    manager.encounterSteps = random.randint(10, 20)
                    manager.encounterStepCounter = 0
                    responseTime = manager.react_flash(480)
                    if responseTime < 320:
                        self.nextScreen = "map"
                        return
                    elif responseTime < 480:
                        world.attributes["player"].add_passive(manager.load_from_db("passives", "Shaken"))
                        self.nextScreen = "map"
                        return
                    else:
                        manager.load_encounter(int(mapCollision[world.attributes["player"].y][world.attributes["player"].x].split(";")[0]))
                        self.nextScreen = "battle"
                        return

            if option == settings.interactBind:
                if portal[2] == "map":
                    mapName = portal[3]
                    world.attributes["player"].x = portal[4]
                    world.attributes["player"].y = portal[5]
                elif portal[2] == "town":
                    manager.town = portal[3]
                    self.nextScreen = "town"
                    return
                elif portal[2] == "location":
                    world.attributes["player"].location = portal[3]
                    self.nextScreen = "location"
                    return
            elif option == "h":
                manager.hunt = not manager.hunt
            elif self.code(option):
                return

    def town(self):
        while 1:
            self.returnScreen = "map"
            text.clear()
            text.background()
            Image("screen/Town").show_at_description()
            text.header(manager.town.title())
            text.move_cursor(1, 3)
            world.attributes["player"].show_stats()

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
            text.background()
            text.header("Inn")

            price = 5 + world.attributes["player"].level * 2
            text.move_cursor(3, 4)
            print(f'Price to rest: {text.gp}{text.reset} {price}')

            text.options(["Rest", text.darkgray + "Quest", text.darkgray + "Gamble"])
            option = control.get_input("alphabetic", options = "r")

            if option == "r":
                if world.attributes["player"].gold >= price:
                    sound.play_sound("rest")
                    world.attributes["player"].gold -= price
                    world.attributes["player"].hp = world.attributes["player"].stats["max hp"]
                    world.attributes["player"].mp = world.attributes["player"].stats["max mp"]
                    text.slide_cursor(1, 3)
                    print("You fell well rested. HP and MP restored to full, ")
                    world.attributes["player"].add_passive(manager.load_from_db("passives", "Well Rested"))
                    control.press_enter()
                else:
                    text.slide_cursor(1, 3)
                    print(f'{text.lightred} You do not have enough gold to rest.')
                    control.press_enter()
            elif self.code(option):
                return

    def store(self):
        while 1:
            self.returnScreen = "town"
            text.clear()
            text.background()
            Image("screen/Store").show_at_description()
            text.header(self.storeType.capitalize())

            storeData = manager.stores[manager.town][self.storeType]
            itemList = []

            for item in storeData["inventory"]:
                try:
                    itemList.append(manager.load_from_db("items", item))
                except:
                    pass

            next = len(itemList) > self.page * 10
            previous = self.page > 1

            if self.storeType != "general":
                text.print_at_loc("Equipment:", 3, 4)
                print("")
                for i in range(len(Globals.slotList)):
                    if world.attributes["player"].equipment[Globals.slotList[i]] != "":
                        text.slide_cursor(0, 3)
                        print(f'  - {world.attributes["player"].equipment[Globals.slotList[i]].get_name()}')
                text.slide_cursor(1, 3)
            else:
                text.move_cursor(3, 4)
            print(f'{text.gp}{text.reset} {world.attributes["player"].gold}\n')

            for i in range(-10 + 10*self.page, 10*self.page if 10*self.page < len(itemList) else len(itemList)):
                quantity = itemList[i].type in Globals.stackableItems
                text.slide_cursor(0, 3)
                print(f'{i}) {itemList[i].get_name(info=True, value=True, quantity=1 if quantity else 0)}')

            if len(itemList) == 0:
                print(f' {text.darkgray}Empty{text.reset}')

            text.slide_cursor(1, 3)
            print(f'Use {settings.moveBind[1]}{settings.moveBind[3]} to switch pages.')
            text.options((["Next"] if next else [])+(["Previous"] if previous else [])+(["Reforge"] if self.storeType == "blacksmith" else [])+["Crafting"])
            option = control.get_input("optionumeric", options=(settings.moveBind[3] if next else "")+(settings.moveBind[1] if previous else "")\
            +("r" if self.storeType == "blacksmith" else "")+"c"+"".join(tuple(map(str, range(0, len(itemList))))))

            if option in tuple(map(str, range(0, len(itemList) + (self.page-1) * 10 + 1))):
                manager.purchaseItem = itemList[int(option) + (self.page-1) * 10]
                self.nextScreen = "purchase"
                return
            elif option == "r":
                self.nextScreen = "reforging"
                return
            elif option == "c":
                self.page = 1
                self.nextScreen = "crafting"
                return
            elif option == settings.moveBind[3]:
                self.page += 1
            elif option == settings.moveBind[1]:
                self.page -= 1
            elif self.code(option):
                return

    def purchase(self):
        while 1:
            self.returnScreen = "store"
            self.nextScreen = self.returnScreen
            text.clear()
            text.background()
            Image("item/" + manager.purchaseItem.name).show_at_description()
            text.header("Purchase")
            text.move_cursor(3, 4)
            print(f'{text.gp}{text.reset} {world.attributes["player"].gold}')
            manager.purchaseItem.show_stats()
            text.slide_cursor(1, 3)
            print(f'Cost: {text.gp}{text.reset} {manager.purchaseItem.value}')
            text.slide_cursor(1, 3)
            print(f'Currently owned: {world.attributes["player"].num_of_items(manager.purchaseItem.name)}')
            text.slide_cursor(0, 3)
            print(f'Type the quantity of items to be purchased ({world.attributes["player"].gold // manager.purchaseItem.value} can be bought).')

            option = control.get_input("numeric")

            print("")

            try:
                option = int(option)
            except:
                pass

            if type(option) is int:
                if option * manager.purchaseItem.value <= world.attributes["player"].gold:
                    sound.play_sound("coin")
                    world.attributes["player"].add_item(manager.purchaseItem, option)
                    if settings.purchaseCost:
                        world.attributes["player"].gold -= option * manager.purchaseItem.value

                    quantity = manager.purchaseItem.type in Globals.stackableItems
                    text.slide_cursor(0, 3)
                    print(f'{manager.purchaseItem.get_name()}{" x" + str(option) if quantity else ""} added to your inventory!')

                    control.press_enter()
                    return
                else:
                    text.slide_cursor(0, 3)
                    print(f'{text.lightred} You cannot buy that many.')
                    control.press_enter()
                    return
            elif self.code(option):
                return

    def crafting(self):
        while 1:
            self.returnScreen = "store"
            text.clear()
            text.background()
            Image("screen/Craft").show_at_description()
            text.header("Crafting")

            recipes = []
            for recipe in manager.recipes:
                addRecipe = False
                for item in recipe["ingredients"]:
                    if world.attributes["player"].num_of_items(item[0]) > 0:
                        addRecipe = True
                        break

                if addRecipe and recipe["type"] == self.storeType:
                    recipes.append(recipe)

            for i in range(-10 + 10*self.page, 10*self.page if 10*self.page < len(recipes) else len(recipes)):
                item = manager.load_from_db("items", recipes[i]["result"])
                quantity = recipe["quantity"] if item.type in Globals.stackableItems else 0
                text.print_at_loc(f'{str(i)[:-1]}({str(i)[-1]}) {item.get_name(info=True, quantity=quantity)}', 3 + int(str(i)[-1]), 4)

            if len(recipes) == 0:
                text.print_at_loc(f' {text.darkgray}No Items Craftable{text.reset}', 3, 4)

            next = len(recipes) > self.page * 10
            previous = self.page > 1

            print("")
            text.slide_cursor(1, 3)
            print(f'Use {settings.moveBind[1]}{settings.moveBind[3]} to switch pages.')
            option = control.get_input("optionumeric", options=(settings.moveBind[3] if next else "")+(settings.moveBind[1] if previous else "")\
            +"".join(tuple(map(str, range(0, len(recipes))))))

            if option in tuple(map(str, range(0, len(recipes) + (self.page-1) * 10 + 1))):
                logger.log(recipes, int(option) + (self.page-1) * 10)
                manager.craftRecipe = recipes[int(option) + (self.page-1) * 10]
                self.nextScreen = "craft"
                return
            elif option == settings.moveBind[3]:
                self.page += 1
            elif option == settings.moveBind[1]:
                self.page -= 1
            elif self.code(option):
                return

    def craft(self):
        while 1:
            self.returnScreen = "crafting"
            self.nextScreen = self.returnScreen
            text.clear()
            text.background()
            text.header("Craft " + manager.craftRecipe["result"])

            manager.craftItem = manager.load_from_db("items", manager.craftRecipe["result"])

            text.move_cursor(2, 1)
            manager.craftItem.show_stats()
            text.slide_cursor(1, 3)
            print(f'Value: {text.gp}{text.reset} {manager.craftItem.value}')

            craftable = True
            numCraftable = 99999999
            text.slide_cursor(0, 3)
            print("Requires:")
            text.slide_cursor(1, 0)
            for i in range(len(manager.craftRecipe["ingredients"])):
                playerIngredientCount = world.attributes["player"].num_of_items(manager.craftRecipe["ingredients"][i][0])
                recipeIngredientCount = manager.craftRecipe["ingredients"][i][1]
                if playerIngredientCount < recipeIngredientCount:
                    craftable = False
                    numCraftable = 0
                elif playerIngredientCount // recipeIngredientCount < numCraftable:
                    numCraftable = playerIngredientCount // recipeIngredientCount
                ingredient = manager.load_from_db("items", manager.craftRecipe["ingredients"][i][0])
                text.slide_cursor(0, 3)
                print(f'{recipeIngredientCount}x {ingredient.get_name()} ({playerIngredientCount}/{recipeIngredientCount})')

            if manager.craftItem.type == "equipment" and craftable:
                numCraftable = 1

            text.slide_cursor(1, 3)
            print(f'Type the quantity of items to be crafted ({numCraftable} craftable)')
            option = control.get_input("numeric")

            try:
                option = int(option)
            except:
                pass

            if type(option) is int:
                if option <= numCraftable:
                    if settings.craftCost:
                        for item in manager.craftRecipe["ingredients"]:
                            world.attributes["player"].remove_item(manager.load_from_db("items", item[0]), item[1])
                    world.attributes["player"].add_item(manager.craftItem, manager.craftRecipe["quantity"] * option)

                    if manager.craftItem.type in Globals.stackableItems:
                        quantity = True
                    else:
                        quantity = False
                    text.slide_cursor(1, 3)
                    print(f'{manager.craftItem.get_name()}{" x" + str(manager.craftRecipe["quantity"] * option) if quantity else ""} added to your inventory!')
                    control.press_enter()
                    return
                else:
                    text.slide_cursor(1, 3)
                    print(f'{text.lightred}You cannot craft that many.')
                    control.press_enter()
            elif self.code(option):
                return

    def market(self):
        while 1:
            self.returnScreen = "town"
            text.clear()
            text.background()
            Image("screen/Store").show_at_description()
            text.header("Flea Market")
            text.move_cursor(3, 4)
            print("Choose an item to sell.")
            text.slide_cursor(1, 0)

            for i in range((self.page - 1) * 10, min(self.page * 10, len(world.attributes["player"].inventory))):
                text.slide_cursor(0, 3)
                quantity = world.attributes["player"].inventory[i][0].type != "equipment"
                print(f' {str(i)[:-1]}({str(i)[-1]}) {world.attributes["player"].inventory[i][0].get_name(info=True, value=True, quantity=(world.attributes["player"].inventory[i][1] if quantity else 0))}')

            if len(world.attributes["player"].inventory) == 0:
                text.slide_cursor(0, 3)
                print(f' {text.darkgray}Empty{text.reset}')

            next = len(world.attributes["player"].inventory) > self.page * 10
            previous = self.page > 1

            text.options((["Next"] if next else []) + (["Previous"] if previous else []))
            option = control.get_input("optionumeric", options=("n" if next else "")+("p" if previous else "")\
            +"".join(tuple(map(str, range(0, len(world.attributes["player"].inventory))))))

            if option in tuple(map(str, range(0, len(world.attributes["player"].inventory) + (self.page-1) * 10 + 1))):
                manager.sellItem = world.attributes["player"].inventory[int(option) + (self.page - 1) * 10][0]
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
            text.background()
            Image("item/" + manager.sellItem.name).show_at_description()
            text.header("Sell " + manager.sellItem.name)

            text.move_cursor(2, 1)
            manager.sellItem.show_stats()

            text.slide_cursor(1, 3)
            print(f'{text.gp}{text.reset} {world.attributes["player"].gold}')
            if manager.sellItem.type != "equipment":
                text.slide_cursor(1, 3)
                print(f'Currently owned: {world.attributes["player"].num_of_items(manager.sellItem.name)}')
            text.slide_cursor(1, 3)
            print(f'Sell Value: {text.gp}{text.reset} {round(manager.sellItem.value * 0.7)}')
            text.slide_cursor(0, 3)
            print(f'Type the quantity of items to be sold ({world.attributes["player"].num_of_items(manager.sellItem.name)} can be sold).')

            option = control.get_input("numeric")

            print("")

            try:
                option = int(option)
            except:
                pass

            if type(option) is int:
                if option <= world.attributes["player"].num_of_items(manager.sellItem.name):
                    sound.play_sound("coin")
                    world.attributes["player"].remove_item(manager.sellItem, option)
                    world.attributes["player"].gold += round(manager.sellItem.value * 0.7) * option

                    quantity = manager.sellItem.type in Globals.stackableItems
                    text.slide_cursor(1, 3)
                    print(f'Sold {manager.sellItem.get_name()}{" x" + str(option) if quantity else ""}.')

                    control.press_enter()
                    return
                else:
                    quantity = manager.sellItem.type in Globals.stackableItems
                    text.slide_cursor(1, 3)
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
            text.background()
            Image("screen/Character").show_at_description()
            text.header("Character")
            text.move_cursor(1, 1)
            world.attributes["player"].show_stats()

            text.options(["Inventory", "Equipment", "Quests", "Passives", "Stats"])
            option = control.get_input("alphabetic", options="ieqps")

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
            elif option == "p":
                self.page = 1
                self.nextScreen = "passives"
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
            text.background()
            Image("screen/Inventory").show_at_description()
            text.header("Inventory")
            print("")

            for i in range((self.page - 1) * 10, min(self.page * 10, len(world.attributes["player"].inventory))):
                item = world.attributes["player"].inventory[i]
                if i >= 100:
                    just = ""
                elif i >= 10:
                    just = " "
                else:
                    just = "  "
                text.print_at_loc(f'{str(i)[:-1]}({str(i)[-1]}) {just}{item[0].get_name(info=True, quantity=item[1])}', 3 + int(str(i)[-1]), 4)

            if len(world.attributes["player"].inventory) == 0:
                text.print_at_loc(f'{text.darkgray}Empty{text.reset}', 3, 4)

            print("")

            next = len(world.attributes["player"].inventory) > self.page * 10
            previous = self.page > 1

            text.slide_cursor(1, 3)
            print(f'Use {settings.moveBind[1]}{settings.moveBind[3]} to switch pages.')
            option = control.get_input("optionumeric", options=(settings.moveBind[3] if next else "")+(settings.moveBind[1] if previous else "")\
            +"".join(tuple(map(str, range(0, len(world.attributes["player"].inventory))))))

            if option in tuple(map(str, range(0, len(world.attributes["player"].inventory) + (self.page-1) * 10 + 1))):
                manager.inspectItem = world.attributes["player"].inventory[int(option) + (self.page - 1) * 10][0]
                manager.inspectItemEquipped = False
                self.nextScreen = "inspect"
                return
            elif option == settings.moveBind[3]:
                self.page += 1
            elif option == settings.moveBind[1]:
                self.page -= 1
            elif self.code(option):
                return

    def equipment(self):
        while 1:
            self.returnScreen = "character"
            text.clear()
            text.background()
            Image("screen/Equipment").show_at_description()
            text.header("Equipment")
            print("")

            for i in range(len(Globals.slotList)):
                text.print_at_loc(f'{i}) {Globals.slotList[i].capitalize()}', 3 + i, 4)
                if world.attributes["player"].equipment[Globals.slotList[i]]:
                    text.print_at_loc(f'{world.attributes["player"].equipment[Globals.slotList[i]].get_name()}', 3 + i, 14)
                else:
                    text.print_at_loc(f'{text.darkgray}Empty{text.reset}', 3 + i, 14)
            print("")

            option = control.get_input("numeric", options="".join(tuple(map(str, range(0, len(Globals.slotList))))))

            if option in tuple(map(str, range(0, len(Globals.slotList)))) and world.attributes["player"].equipment[Globals.slotList[int(option)]] != "":
                manager.inspectItem = world.attributes["player"].equipment[Globals.slotList[int(option)]]
                manager.inspectItemEquipped = True
                manager.inspectSlot = Globals.slotList[int(option)]
                self.nextScreen = "inspect"
                return
            elif self.code(option):
                return

    def inspect(self):
        while 1:
            self.returnScreen = self.oldScreen
            self.nextScreen = self.returnScreen
            text.clear()
            text.background()
            Image("item/" + manager.inspectItem.name).show_at_description()

            if manager.inspectItemEquipped:
                manager.inspectItem.update()
            world.attributes["player"].update_stats()

            text.header("Inspect " + manager.inspectItem.type.capitalize())
            text.move_cursor(2, 1)
            manager.inspectItem.show_stats()
            text.slide_cursor(1, 3)
            print(f'Value: {text.gp} {text.reset}{manager.inspectItem.value}')

            if manager.inspectItem.type == "equipment":
                text.options((["Unequip"] if manager.inspectItemEquipped else ["Equip", "Discard"])+["More Info"])
                option = control.get_input("alphabetic", options=("u" if manager.inspectItemEquipped else "ed")+"m", silentOptions=("u" if manager.inspectItemEquipped else "e"))
            elif manager.inspectItem.type == "consumable":
                text.options((["Use"] if manager.inspectItem.target == "self" else [])+["Discard"])
                option = control.get_input("alphabetic", options=("u" if manager.inspectItem.target == "self" else "")+"d")
            elif manager.inspectItem.type == "modifier":
                text.options(["Use", "Discard"])
                option = control.get_input("alphabetic", options="ud")
            else:
                text.options(["Discard"])
                option = control.get_input("alphabetic", options="d")

            if option == "u" and manager.inspectItem.type == "equipment":
                sound.play_sound("equip")
                world.attributes["player"].unequip(manager.inspectSlot)
                return
            elif option == "u" and manager.inspectItem.type == "consumable" and manager.inspectItem.target == "self":
                manager.inspectItem.use(world.attributes["player"], world.attributes["player"])
                world.attributes["player"].remove_item(manager.inspectItem)
                control.press_enter()
                if world.attributes["player"].num_of_items(manager.inspectItem.name) <= 0:
                    return
            elif option == "u" and manager.inspectItem.type == "modifier":
                self.nextScreen = "apply_modifier"
                return
                s_applyModifier(manager.inspectItem)
                if "infinite" not in manager.inspectItem.tags:
                    world.attributes["player"].remove_item(manager.inspectItem)
                if world.attributes["player"].num_of_items(manager.inspectItem.name) <= 0:
                    return
            elif option == "e" and manager.inspectItem.type == "equipment":
                sound.play_sound("equip")
                world.attributes["player"].equip(manager.inspectItem)
                return
            elif option == "d":
                if world.attributes["player"].num_of_items(manager.inspectItem.name) > 1:
                    while 1:
                        text.clear()
                        text.header("Quantity")
                        print(f'\n Type the quantity to discard (1-{world.attributes["player"].num_of_items(manager.inspectItem.name)})')

                        option = control.get_input("numeric")

                        if option in tuple(map(str, range(1, world.attributes["player"].num_of_items(manager.inspectItem.name)+1))):
                            world.attributes["player"].remove_item(manager.inspectItem, int(option))
                            return
                        elif self.code(option):
                            break
                else:
                    world.attributes["player"].remove_item(manager.inspectItem)
                    break
            elif option == "m":
                text.clear_main()
                text.move_cursor(2, 1)

                manager.inspectItem.show_stats_detailed()

                control.press_enter()
            elif self.code(option):
                return

    def apply_modifier(self):
        while 1:
            self.returnScreen = "inventory"
            text.clear()
            text.background()
            Image("item/" + manager.inspectItem.name).show_at_description()
            text.header("Apply Modifier")

            slots = manager.inspectItem.slot.split(", ")

            for i in range(len(slots)):
                text.print_at_loc(f'{i}) {slots[i].capitalize()}', 3 + i, 4)
                if world.attributes["player"].equipment[slots[i]]:
                    text.print_at_loc(f'{world.attributes["player"].equipment[slots[i]].get_name()} {world.attributes["player"].equipment[slots[i]].modifier.get_name()}', 3 + i, 14)
                else:
                    text.print_at_loc(f'{text.darkgray}Empty{text.reset}', 3 + i, 14)

            option = control.get_input("numeric", options="".join(tuple(map(str, range(0, len(slots))))))

            if option in tuple(map(str, range(0, len(slots)))) and world.attributes["player"].equipment[slots[int(option)]]:
                manager.inspectItem.use(None, world.attributes["player"].equipment[slots[int(option)]], True)
                if "infinite" not in manager.inspectItem.tags:
                    world.attributes["player"].remove_item(manager.inspectItem)
                if world.attributes["player"].num_of_items(manager.inspectItem.name) <= 0:
                    self.nextScreen = "inventory"
                    return
                break
            elif self.code(option):
                return

    def passives(self):
        while 1:
            self.returnScreen = "character"
            text.clear()
            text.background()
            Image("screen/Passives").show_at_description()
            text.move_cursor(3, 1)

            for i in range((self.page - 1) * 10, min(self.page * 10, len(world.attributes["player"].passives))):
                text.slide_cursor(0, 3)
                print(f'{str(i)[:-1]}({str(i)[-1]}) {world.attributes["player"].passives[i].get_name(turns=True)}')

            if len(world.attributes["player"].passives) == 0:
                text.slide_cursor(0, 3)
                print(f'{text.darkgray}No Passives{text.reset}')

            next = len(world.attributes["player"].passives) > self.page * 10
            previous = self.page > 1

            text.slide_cursor(1, 3)
            print(f'Use {settings.moveBind[1]}{settings.moveBind[3]} to switch pages.')
            option = control.get_input("optionumeric", options=(settings.moveBind[3] if next else "")+(settings.moveBind[1] if previous else "")\
            +"".join(tuple(map(str, range(0, len(world.attributes["player"].passives))))))

            if option in tuple(map(str, range(0, len(world.attributes["player"].passives) + (self.page-1) * 10 + 1))):
                manager.inspectPassive = world.attributes["player"].passives[int(option) + (self.page - 1) * 10]
                self.nextScreen = "inspect_passive"
                return
            elif option == settings.moveBind[3]:
                self.page += 1
            elif option == settings.moveBind[1]:
                self.page -= 1
            elif self.code(option):
                return

    def stats(self):
        while 1:
            self.nextScreen = "character"
            text.clear()
            text.background()
            Image("screen/Stats").show_at_description()
            text.header("Stats")

            stats = world.attributes["player"].stats.copy()
            stats.pop("max hp")
            stats.pop("max mp")
            stats.pop("attack")

            statNamePad = len(max(world.attributes["player"].stats, key=len)) + 1
            statValuePad = len(max([str(world.attributes["player"].stats[stat]) for stat in stats], key=len))

            text.move_cursor(1, 1)
            world.attributes["player"].show_stats(passives=False)
            text.slide_cursor(1, 3)
            print(f'{"Attack".ljust(statNamePad)}: {(str(world.attributes["player"].stats["attack"][0]) + " - " + str(world.attributes["player"].stats["attack"][1])).ljust(statValuePad)}')

            for stat in stats:
                if world.attributes["player"].baseStats[stat] <= world.attributes["player"].stats[stat]:
                    changeString = "+"
                else:
                    changeString = "-"
                text.slide_cursor(0, 3)
                print(f'{stat.capitalize().ljust(statNamePad)}: {str(world.attributes["player"].stats[stat]).ljust(statValuePad)} ({changeString}{world.attributes["player"].stats[stat] - world.attributes["player"].baseStats[stat]})')

            control.press_enter()
            return

    def inspect_passive(self):
        while 1:
            self.returnScreen = "passives"
            self.nextScreen = self.returnScreen
            text.clear()
            text.background()
            text.header("Inspect passive")
            text.move_cursor(3, 4)
            print(f'Name: {manager.inspectPassive.get_name(turns=True)}')
            text.slide_cursor(0, 3)
            print(f'Description: {manager.inspectPassive.description}')
            text.slide_cursor(1, 0)
            for effect in manager.inspectPassive.effect:
                effect.show_stats()

            control.get_input("none")
            return

    def rest(self):
        self.nextScreen = self.returnScreen
        hp = math.floor(world.attributes["player"].stats["max hp"] * 0.85)
        mp = math.floor(world.attributes["player"].stats["max mp"] * 0.85)
        if world.attributes["player"].hp >= hp and world.attributes["player"].mp >= mp:
            return
        if hp > world.attributes["player"].hp:
            world.attributes["player"].hp = hp
        if mp > world.attributes["player"].mp:
            world.attributes["player"].mp = mp
        sound.play_sound("rest")


if __name__ == "__main__":
    if Globals.system == "Windows":
        import win32api
        os.system("title Magyka")
    else:
        import signal

    try:
        manager = Manager()
        screen = Screen()
    except Exception as err:
        text.clear()
        text.move_cursor(1, 1)
        traceback.print_exc()
        logger.log(traceback.format_exc())
        control.press_enter()
