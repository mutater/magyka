from random import randint
import math, copy
from .Globals import *

def ifNone(value, backup):
    if not value == None: return value
    else: return backup

def ifIn(key, container, backup):
    if key in container: return container[key]
    else: return backup

class Entity():
    def __init__(self, name, hp, mp, level, statValues):
        self.name, self.hp, self.mp, self.level = name, hp, mp, level
        self.stats = {
            "attack": [1, 1],
            "armor": 0,
            "strength": 0,
            "intelligence": 0,
            "vitality": 0,
            "crit": 4,
            "hit": 90,
            "dodge": 5,
            "max hp": hp,
            "max mp": mp
        }
        self.stats.update(dict((stat, statValues[stat]) for stat in self.stats if stat in statValues))
        self.baseStats = self.stats.copy()
        self.statChanges = dict((stat, [[0, 0], [0, 0], 0]) for stat in self.stats)

        self.equipment = {"": ""}
        self.passives = []
        self.guard = ""

    def updateStats(self):
        bufferhp, buffermp = self.hp - self.stats["max hp"], self.mp - self.stats["max mp"]
        for statName in self.stats:
            self.statChanges[statName] = [[0, 0], [0, 0], -1]
            for slot in self.equipment:
                if self.equipment[slot] == "": continue
                for effect in self.equipment[slot]["effect"]:
                    if effect["type"] != statName: continue
                    if statName == "attack": self.stats[statName] = effect["value"]
                    elif "=" in effect: self.statChanges[statName][2] = effect["value"] if effect["value"] < self.statChanges[statName][2] else self.statChanges[statName][2]
                    elif "*" in effect: self.statChanges[statName][0][1] += effect["value"]
                    else: self.statChanges[statName][0][0] += effect["value"]
        for passive in self.passives:
            if not type(passive["effect"]) is list: passive["effect"] = [passive["effect"]]
            for effect in passive["effect"]:
                if effect["type"] not in self.stats or effect["type"] == "attack": continue
                if "=" in effect: self.statChanges[effect["type"]][2] = effect["value"] if effect["value"] < self.statChanges[effect["type"]][2] else self.statChanges[effect["type"]][2]
                elif "*" in effect: self.statChanges[effect["type"]][1][1] += effect["value"]
                else: self.statChanges[effect["type"]][1][0] += effect["value"]
        for statName in self.stats:
            if statName != "attack":
                self.stats[statName] = 0
                self.stats[statName] = self.baseStats[statName] + self.statChanges[statName][0][0] + self.statChanges[statName][1][0]
                self.stats[statName] += round(self.baseStats[statName] * (self.statChanges[statName][0][1] + self.statChanges[statName][1][1]) / 100)
                if self.statChanges[statName][2] >= 0: self.stats[statName] = self.statChanges[statName][2]
        self.hp, self.mp = self.stats["max hp"] + bufferhp, self.stats["max mp"] + buffermp
        if self.hp <= 0 and bufferhp != 0: self.hp = 1
        if self.mp <= 0 and buffermp != 0: self.mp = 0

    def defend(self, effect, stats = {"hit": 100, "crit": 0}, passive = False):
        effect = copy.deepcopy(effect)
        text = ""
        if effect["type"] in ("-hp", "-mp", "-all", "passive"):
            if effect["type"] != "passive":
                amount, a, r, v = [([0, 0] if effect["type"] == "-all" else 0) for i in range(4)]
                crit = 2 if randint(1, 100) <= ifNone(ifIn("crit", effect, None), ifIn("crit", stats, 0)) else 1
                critical = 'critical ' if crit == 2 else ''
            h = 1 if randint(1, 100) <= ifNone(ifIn("hit", effect, None), ifIn("hit", stats, 100)) else 0
            d = 0 if randint(1, 100) <= self.stats["dodge"] * ifNone(ifIn("dodge", effect, None), 1) else 1

            deflect = True if self.guard == "deflect" else False

            if self.guard == "block": return f'but {self.name} blocks the attack.'
            if self.guard == "counter": return
            if not h: return 'but misses.'
            if not d: return f'but {self.name} dodges.'

            if effect["type"] == "-all":
                if type(effect["value"][0]) is list: a[0] = randint(effect["value"][0][0], effect["value"][0][1])
                else: a[0] = effect["value"][0]
                if type(effect["value"][1]) is list: a[0] = randint(effect["value"][1][0], effect["value"][1][1])
                else: a[0] = effect["value"][1]
                r = (self.stats["armor"] / 2 + self.stats["vitality"]) * ifNone(ifIn("resist", effect, None), ifIn("resist", stats, 1))
                v = [randint(80, 120) / 100, randint(80, 120) / 100]

                amount = [round((a[0] - r) * v[0] * crit), round((a[1] - r) * v[1] * crit)]
                if deflect: amount = [round(amount[0] / 2), round(amount[1] / 2)]
                amount = [1 if amount[0] < 1 else amount[0], 1 if amount[1] < 1 else amount[1]]

                self.hp -= amount[0]*h*d
                if self.hp < 0: self.hp = 0
                self.mp -= amount[1]*h*d
                if self.mp < 0: self.mp = 0
                text = f'dealing {c("red")}{amount[0]} ♥{reset} and {c("blue")}{amount[1]} ♦{reset} {critical}damage'
            elif effect["type"] in ("-hp", "-mp"):
                if type(effect["value"]) is list: a = randint(effect["value"][0], effect["value"][1])
                else: a = effect["value"]
                r = (self.stats["armor"] / 2 + self.stats["vitality"]) * ifNone(ifIn("resist", effect, None), ifIn("resist", stats, 1))
                v = randint(80, 120) / 100 if ifNone(ifIn("variance", effect, None), False) else 1

                amount = round((a - r) * v * crit)
                if deflect: amount = round(amount / 2)
                amount = 1 if amount < 1 else amount

                if effect["type"] == "-hp":
                    self.hp -= amount*h*d
                    if self.hp < 0: self.hp = 0
                    text = f'dealing {c("red")}{amount} ♥{reset} {critical}damage'
                else:
                    self.mp -= amount*h*d
                    if self.mp < 0: self.mp = 0
                    text = f'dealing {c("blue")}{amount} ♦{reset} {critical}damage'
            elif effect["type"] == "passive":
                passiveFound = False
                if type(effect["turns"]) is list: turns = randint(effect["turns"][0], effect["turns"][1])
                else: turns = effect["turns"]
                effect["turns"] = turns
                for p in self.passives:
                    if effect["name"] == p["name"]:
                        passiveFound = True
                        p["turns"] = turns
                        break
                if not passiveFound: self.passives.append(effect)
                text = f'applying {c("light green" if effect["buff"] == True else "light red")}{effect["name"]}{reset} ({effect["turns"]})'
        elif effect["type"] in ("hp", "mp", "all"):
            if effect["type"] == "all":
                if "*" in effect: amount = [(effect["value"][0] / 100) * self.stats["max hp"], (effect["value"][1] / 100) * self.stats["max mp"]]
                else: amount = [effect["value"][0], effect["value"][1]]
                amount = [1 if amount[0] < 1 else amount[0], 1 if amount[1] < 1 else amount[1]]
                if amount[0] + self.hp > self.stats["max hp"]: amount[0] = self.stats["max hp"] - self.hp
                if amount[1] + self.mp > self.stats["max mp"]: amount[1] = self.stats["max mp"] - self.mp

                self.hp += amount[0]
                self.mp += amount[1]
                text = f'healing {c("red")}{amount[0]} ♥{reset} and {c("blue")}{amount[1]} ♦{reset}'
            else:
                if "*" in effect: amount = (effect["value"] / 100) * self.stats[stat]
                else: amount = effect["value"]
                if amount < 1: amount = 1

                if effect["type"] == "hp":
                    if amount + self.hp > self.stats["max hp"]: amount = self.stats["max hp"] - self.hp
                    self.hp += amount
                    text = f'healing {c("red")}{amount} ♥{reset}'
                else:
                    if amount + self.mp > self.stats["max mp"]: amount = self.stats["max mp"] - self.mp
                    self.mp += amount
                    text = f'healing {c("blue")}{amount} ♦{reset}'
        if passive != False:
            if type(passive) is list:
                for i in range(len(passive)):
                    text += ", "
                    if i == len(passive) - 1: text += "and "
                    passive[i].update({"dodge": 0, "hit": 100})
                    text += self.defend(passive[i])
            else:
                text += " and "
                passive.update({"dodge": 0, "hit": 100})
                text += self.defend(passive)
                print(self.passives)
        else: text += "."
        return text

    def update(self):
        self.updateStats()
        text = []
        for passive in self.passives:
            for effect in passive["effect"]:
                if effect["type"] in ("-hp", "-mp", "-all", "hp", "mp", "all"):
                    prefix = f'\n {c("light green" if passive["buff"] else "light red")}{passive["name"]}{reset} persists, '
                    suffix = self.defend(effect)
                    text.append(prefix + suffix)
            
            passive["turns"] -= 1
            if passive["turns"] <= 0:
                self.passives.remove(passive)
                text.append(f'\n {passive["name"]} wears off.')
                continue
        return text

    def attack(self):
        attackSkill = {"type": "-hp", "value": [self.stats["attack"][0] + self.stats["strength"], self.stats["attack"][1] + self.stats["strength"]], "crit": self.stats["crit"], "hit": self.stats["hit"]}
        return attackSkill

class Player(Entity):
    def __init__(self, equipment):
        super().__init__("", 7, 10, 1, [])
        self.xp, self.mxp, self.gold = 0, 10, 0
        self.location = "fordsville"

        self.inventory = []
        self.recipes = []
        self.equipment = equipment
        self.magic = None
        self.updateStats()

    def getDrops(self, xp, gold, items = []):
        self.xp += xp
        self.gold += gold
        for item in items:
            self.addItem(item[0], item[1])
        if self.xp >= self.mxp:
            while self.xp >= self.mxp:
                xp = self.xp - self.mxp
                self.level += 1
                self.xp = xp
                self.mxp = math.ceil(self.mxp * 1.2)
                self.baseStats["max hp"] = math.ceil(self.baseStats["max hp"] * 1.1)
                self.baseStats["max mp"] = math.ceil(self.baseStats["max mp"] * 1.1)
                self.updateStats()
                self.hp = self.stats["max hp"]
                self.mp = self.stats["max mp"]
            return True
        return False

    def numOfItems(self, name):
        sum = 0
        for item in self.inventory:
            if item[0]["name"] == name: sum += item[1]
        return sum

    def addItem(self, item, quantity = 1):
        if item["type"] in stackableItems:
            for i in self.inventory:
                if i[0]["name"] == item["name"]:
                    i[1] += quantity
                    return
            self.inventory.append([item, quantity])
            return
        else:
            for i in range(quantity):
                self.inventory.append([item, 1])
            return

    def removeItem(self, item, quantity = 1):
        if item["type"] in stackableItems:
            for i in self.inventory:
                if i[0]["name"] == item["name"]:
                    i[1] -= quantity
                    if i[1] <= 0: self.inventory.remove([i[0], i[1]])
                    return
        else:
            for i in range(quantity):
                try:
                    self.inventory.remove([item, 1])
                except:
                    return
            return

    def unequip(self, slot):
        self.addItem(self.equipment[slot])
        self.equipment[slot] = ""
        self.updateStats()

    def equip(self, item):
        if self.equipment[item["slot"]] != "": self.unequip(item["slot"])
        self.equipment[item["slot"]] = item
        self.removeItem(item)
        if item["slot"] == "tome": self.magic = item["effect"]
        self.updateStats()

    def get_magic(self):
        magicSkill = copy.deepcopy(self.magic)
        for i in range(len(magicSkill)):
            if magicSkill[i]["type"] in ("all", "-all"):
                if type(magicSkill[i]["value"][0]) is list: magicSkill[i]["value"][0] = [magicSkill[i]["value"][0][0] + self.stats["intelligence"], magicSkill[i]["value"][0][1] + self.stats["intelligence"]]
                else: magicSkill[i]["value"][0] += self.stats["intelligence"]
                if type(magicSkill[i]["value"][1]) is list: magicSkill[i]["value"][1] = [magicSkill[i]["value"][1][0] + self.stats["intelligence"], magicSkill[i]["value"][1][1] + self.stats["intelligence"]]
                else: magicSkill[i]["value"][1] += self.stats["intelligence"]
            else:
                if type(magicSkill[i]["value"]) is list: magicSkill[i]["value"] = [magicSkill[i]["value"][0] + self.stats["intelligence"], magicSkill[i]["value"][1] + self.stats["intelligence"]]
                else: magicSkill[i]["value"] += self.stats["intelligence"]
        return magicSkill

class Enemy(Entity):
    def __init__(self, kwargs):
        super().__init__(kwargs["name"], kwargs["hp"], kwargs["mp"], kwargs["level"], kwargs["stats"])
        self.xp = kwargs["xp"]
        self.gold = kwargs["gold"]
        self.items = kwargs["items"]
        self.updateStats()
        self.attackSound = kwargs["attackSound"]
        self.attackVerb = kwargs["attackVerb"]
        self.magic = kwargs.get("magic")
        self.levelDifference = 0
