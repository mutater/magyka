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
        self.name, self.__hp, self.__mp, self.level = name, hp, mp, level
        self.__stats = {
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
        self.__stats.update(dict((stat, statValues[stat]) for stat in self.__stats if stat in statValues))
        self.baseStats = self.__stats.copy()
        self.statChanges = dict((stat, [[0, 0], [0, 0], 0]) for stat in self.__stats)

        self.equipment = {"": ""}
        self.passives = []
        self.guard = ""

    def getHp(self):
        return self.__hp
    
    def setHp(self, hp):
        if hp >= 0: self.__hp = hp
        else: self.__hp = 0
    
    hp = property(getHp, setHp)
    
    def getMp(self):
        return self.__mp
    
    def setMp(self, mp):
        if mp >= 0: self.__mp = mp
        else: self.__mp = 0

    mp = property(getMp, setMp)

    def getStats(self):
        return copy.deepcopy(self.__stats)
    
    stats = property(getStats)

    def updateStats(self):
        bufferhp, buffermp = self.__hp - self.__stats["max hp"], self.__mp - self.__stats["max mp"]
        oldMaxHp, oldMaxMp = self.stats["max hp"], self.stats["max mp"]
        effects = []
        self.statChanges = {statName: [[0, 0], [0, 0], -1] for statName in self.__stats}
        for slot in self.equipment:
            if self.equipment[slot] == "":
                if slot == "weapon": self.__stats["attack"] = [1, 1]
                continue
            effects += self.equipment[slot]["effect"]
            if slot == "weapon":
                for effect in self.equipment["weapon"]["effect"]:
                    if effect["type"] == "attack": self.__stats["attack"] = copy.deepcopy(effect["value"])
        
        for passive in self.passives:
            if not type(passive["effect"]) is list: passive["effect"] = [passive["effect"]]
            effects += passive["effect"]
        
        for effect in effects:
            if effect["type"] not in self.__stats or effect["type"] == "attack": continue
            if "=" in effect: self.statChanges[effect["type"]][2] = effect["value"] if effect["value"] < self.statChanges[effect["type"]][2] else self.statChanges[effect["type"]][2]
            elif "*" in effect: self.statChanges[effect["type"]][1][1] += effect["value"]
            else: self.statChanges[effect["type"]][1][0] += effect["value"]
        
        for statName in self.__stats:
            if statName != "attack":
                self.__stats[statName] = 0
                self.__stats[statName] = self.baseStats[statName] + self.statChanges[statName][0][0] + self.statChanges[statName][1][0]
                self.__stats[statName] += round(self.baseStats[statName] * (self.statChanges[statName][0][1] + self.statChanges[statName][1][1]) / 100)
                if self.statChanges[statName][2] >= 0: self.__stats[statName] = self.statChanges[statName][2]
        
        self.__hp, self.__mp = self.__stats["max hp"] + bufferhp, self.__stats["max mp"] + buffermp
        if self.__hp <= 0 and bufferhp != 0 and self.__stats["max hp"] - oldMaxHp != 0: self.__hp = 1
        if self.__mp <= 0 and buffermp != 0 and self.__stats["max mp"] - oldMaxMp != 0: self.__mp = 0

    def defend(self, effect, attackerStats={"hit": 100, "crit": 0}, tags=[], passive=False):
        effect = copy.deepcopy(effect)
        text = ""
        hpAmount = 0
        attackerStats["pierce"] = 1
        attackerStats["variance"] = 20
        for i in range(len(tags)):
            tag = tags[i].split(":")
            if tag[0] in ("noMiss", "hit"): attackerStats["hit"] = 100
            elif tag[0] in ("noDodge", "hit"): attackerStats["dodge"] = 1
            elif tag[0] in ("pierce"):
                try: attackerStats["pierce"] = 100 / int(tag[1])
                except: attackerStats["pierce"] = 0
            elif tag[0] in ("variance"):
                try: attackerStats["variance"] = int(tag[1])
                except: attackerStats["variance"] = 20
        
        if effect["type"] in ("-hp", "-mp", "-all", "passive"):
            if effect["type"] != "passive":
                amount, a, r, v = [([0, 0] if effect["type"] == "-all" else 0) for i in range(4)]
                crit = 2 if randint(1, 100) <= ifNone(ifIn("crit", effect, None), ifIn("crit", attackerStats, 0)) else 1
                critical = 'critical ' if crit == 2 else ''
            h = 1 if randint(1, 100) <= ifNone(ifIn("hit", effect, None), ifIn("hit", attackerStats, 100)) else 0
            d = 0 if randint(1, 100) <= self.__stats["dodge"] * ifNone(ifIn("dodge", effect, None), 1) else 1

            deflect = True if self.guard == "deflect" else False

            if self.guard == "block": return f'but {self.name} blocks the attack.', 0
            if self.guard == "counter": return f'but {self.name} counters, ', 0
            if not h: return 'but misses.', 0
            if not d: return f'but {self.name} dodges.', 0

            if effect["type"] == "-all":
                if type(effect["value"][0]) is list: a[0] = randint(effect["value"][0][0], effect["value"][0][1])
                else: a[0] = effect["value"][0]
                if type(effect["value"][1]) is list: a[1] = randint(effect["value"][1][0], effect["value"][1][1])
                else: a[1] = effect["value"][1]
                r = (self.stats["armor"] / 2 + self.stats["vitality"]) / attackerStats["pierce"]
                v = [randint(100 - attackerStats["variance"], 100 + attackerStats["variance"]) / 100, randint(100 - attackerStats["variance"], 100 + attackerStats["variance"]) / 100]

                amount = [round((a[0] - r) * v[0] * crit), round((a[1] - r) * v[1] * crit)]
                if deflect: amount = [round(amount[0] / 2), round(amount[1] / 2)]
                amount = [(1 if amount[0] < 1 else amount[0]), (1 if amount[1] < 1 else amount[1])]

                self.__hp -= amount[0]*h*d
                hpAmount = amount[0]*h*d*-1
                self.__mp -= amount[1]*h*d
                text = 'dealing {c("red")}' + str(amount[0]) + ' ♥{reset} and {c("blue")}' + str(amount[1]) + ' ♦{reset} '+ critical + 'damage'
            elif effect["type"] in ("-hp", "-mp"):
                if type(effect["value"]) is list: a = randint(effect["value"][0], effect["value"][1])
                else: a = effect["value"]
                r = (self.stats["armor"] / 2 + self.stats["vitality"]) / attackerStats["pierce"]
                v = randint(100 - attackerStats["variance"], 100 + attackerStats["variance"]) / 100

                amount = round((a - r) * v * crit)
                if deflect: amount = round(amount / 2)
                amount = 1 if amount < 1 else amount

                if effect["type"] == "-hp":
                    self.__hp -= amount*h*d
                    hpAmount = amount*h*d*-1
                    text = 'dealing {c("red")}' + str(amount) + ' ♥{reset} '+ critical + 'damage'
                else:
                    self.__mp -= amount*h*d
                    text = 'dealing {c("blue")}' + str(amount) + ' ♦{reset} '+ critical + 'damage'
            elif effect["type"] == "passive":
                text = self.addPassive(effect)
        elif effect["type"] in ("hp", "mp", "all"):
            if effect["type"] == "all":
                if "*" in effect: amount = [(effect["value"][0] / 100) * self.__stats["max hp"], (effect["value"][1] / 100) * self.__stats["max mp"]]
                else: amount = [effect["value"][0], effect["value"][1]]
                amount = [1 if amount[0] < 1 else amount[0], 1 if amount[1] < 1 else amount[1]]
                if amount[0] + self.__hp > self.__stats["max hp"]: amount[0] = self.__stats["max hp"] - self.__hp
                if amount[1] + self.__mp > self.__stats["max mp"]: amount[1] = self.__stats["max mp"] - self.__mp

                self.__hp += amount[0]
                hpAmount = amount[0]
                self.__mp += amount[1]
                text = 'healing {c("red")}{amount[0]} ♥{reset} and {c("blue")}{amount[1]} ♦{reset}'
            else:
                if "*" in effect: amount = (effect["value"] / 100) * self.__stats[stat]
                else: amount = effect["value"]
                if amount < 1: amount = 1

                if effect["type"] == "hp":
                    if amount + self.__hp > self.__stats["max hp"]: amount = self.__stats["max hp"] - self.__hp
                    self.__hp += amount
                    hpAmount = amount
                    text = 'healing {c("red")}' + str(amount) + ' ♥{reset}'
                else:
                    if amount + self.__mp > self.__stats["max mp"]: amount = self.__stats["max mp"] - self.__mp
                    self.__mp += amount
                    text = 'healing {c("blue")}' + str(amount) + ' ♦{reset}'
        if passive != False:
            if type(passive) is list:
                for i in range(len(passive)):
                    text += ", "
                    if i == len(passive) - 1: text += "and "
                    text += self.addPassive(passive[i])
            else:
                text += " and "
                text += self.addPassive(passive)
        else: text += "."
        return text, hpAmount

    def addPassive(self, passive):
        passive.update({"dodge": 0, "hit": 100})
        passiveFound = False
        if type(passive["turns"]) is list: turns = randint(passive["turns"][0], passive["turns"][1])
        else: turns = passive["turns"]
        passive["turns"] = turns
        for p in self.passives:
            if passive["name"] == p["name"]:
                passiveFound = True
                p["turns"] = turns
                break
        if not passiveFound: self.passives.append(passive)
        self.updateStats()
        return f'applying {c("light green" if passive["buff"] == True else "light red")}{passive["name"]}{reset} ({passive["turns"]})'

    def update(self):
        self.updateStats()
        text = []
        tempDamage = 0
        for passive in self.passives:
            for effect in passive["effect"]:
                if effect["type"] in ("-hp", "-mp", "-all", "hp", "mp", "all"):
                    prefix = f' {c("light green" if passive["buff"] else "light red")}{passive["name"]}{reset} persists, '
                    suffix, tempDamage = self.defend(effect)
                    tempDamage += tempDamage
                    text.append(prefix + suffix)
            
            passive["turns"] -= 1
            if passive["turns"] <= 0:
                self.passives.remove(passive)
                text.append(f' {passive["name"]} wears off.')
                continue
        return text, tempDamage

    def attack(self):
        attackSkill = {"type": "-hp", "value": [self.__stats["attack"][0] + self.__stats["strength"], self.__stats["attack"][1] + self.__stats["strength"]], "crit": self.__stats["crit"], "hit": self.__stats["hit"]}
        if "weapon" in self.equipment and self.equipment["weapon"] != "":
            for effect in self.equipment["weapon"]["effect"]:
                if effect["type"] == "passive": attackSkill.update({"passive": effect["value"]})
        return attackSkill

class Player(Entity):
    def __init__(self, equipment, mainQuests):
        super().__init__("", 7, 10, 1, [])
        self.__xp, self.mxp, self.gold = 0, 10, 0
        self.levelsGained = 0
        
        self.location = "fordsville"
        self.locations = {"fordsville": []}
        self.quests = []
        self.mainQuests = mainQuests
        for quest in mainQuests:
            quest.update({"main": True})
        self.addQuest(mainQuests[0])
        self.mainQuest = 0
        self.completedQuests = []
        
        self.inventory = []
        self.recipes = []
        self.equipment = equipment
        self.magic = None
        
        self.updateStats()
    
    def getXp(self):
        return self.__xp

    def setXp(self, xp):
        self.__xp = xp
        if xp < self.mxp:
            self.__xp = xp
            return
        while self.__xp >= self.mxp:
            self.__xp -= self.mxp
            self.mxp = math.ceil(self.mxp * 1.2)
            self.baseStats["max hp"] = math.ceil(self.baseStats["max hp"] * 1.1)
            self.baseStats["max mp"] = math.ceil(self.baseStats["max mp"] * 1.1)
            self.updateStats()
            self.__hp = self.stats["max hp"]
            self.__mp = self.stats["max mp"]
            self.level += 1
            self.levelsGained += 1
            
    xp = property(getXp, setXp)

    def addQuest(self, quest):
        for i in range(len(quest["objective"])):
            quest["objective"][i].update({"status": 0, "complete": False})
        if "location" not in quest: quest["location"] = None
        elif len(quest["location"]) == 2: self.locations[quest["location"][0]].append(quest["location"][1])
        self.quests.append(quest)

    def updateQuests(self, enemy = None, item = None, location = None):
        for i in range(len(self.quests)):
            complete = True
            for j in range(len(self.quests[i]["objective"])):
                if self.quests[i]["objective"][j]["type"] == "kill":
                    if enemy and enemy.name == self.quests[i]["objective"][j]["name"]:
                        self.quests[i]["objective"][j]["status"] += 1
                        if self.quests[i]["objective"][j]["status"] >= self.quests[i]["objective"][j]["quantity"]:
                            self.quests[i]["objective"][j]["complete"] = True
                elif self.quests[i]["objective"][j]["type"] == "obtain":
                    if item and item[0]["name"] == self.quests[i]["objective"][j]["name"]:
                        self.quests[i]["objective"][j]["status"] += item[1]
                        if self.quests[i]["objective"][j]["status"] >= self.quests[i]["objective"][j]["quantity"]:
                            self.quests[i]["objective"][j]["complete"] = True
                if not self.quests[i]["objective"][j]["complete"]: complete = False
            if complete:
                self.completedQuests.append(self.quests[i])
                self.finishQuest(i)
    
    def finishQuest(self, index):
        quest = self.quests.pop(index)
        if quest.get("main") != None:
            self.mainQuest += 1
            self.addQuest(self.mainQuests[self.mainQuest])
        if "item" in quest["reward"]:
            for item in quest["reward"]["item"]:
                self.addItem(item[0], item[1])
        if "xp" in quest["reward"]: self.xp += quest["reward"]["xp"]
        if "gold" in quest["reward"]: self.gold += quest["reward"]["gold"]
        if "stat" in quest["reward"]:
            for stat in quest["reward"]["stat"]:
                if stat.get("*"): self.baseStats[stat["type"]] = round(self.baseStats[stat["type"]] * (1 + stat["value"]))
                else: self.baseStats[stat["type"]] += stat["value"]

    def numOfItems(self, name):
        sum = 0
        for item in self.inventory:
            if item[0]["name"] == name: sum += item[1]
        return sum

    def addItem(self, item, quantity = 1):
        self.updateQuests(item=[item, quantity])
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

    def enchantEquipment(self, slot, enchantment):
        enchantmentFound = False
        for e in self.equipment[slot]["enchantments"]:
            if e["name"] == enchantment["name"]:
                enchantmentFound = True
                if e["level"] == enchantment["level"] and e["level"] < 10: e["level"] += 1
                elif e["level"] < enchantment["level"]: e["level"] = enchantment["level"]
                break
        if not enchantmentFound: self.equipment[slot]["enchantments"].append(enchantment)
        self.equipment[slot] = self.updateEquipment(self.equipment[slot])
        self.updateStats()
    
    def modifyEquipment(self, slot, modifier):
        self.equipment[slot]["modifier"] = modifier
        self.equipment[slot] = self.updateEquipment(self.equipment[slot])
        self.updateStats()
    
    def updateEquipment(self, item):
        item = copy.deepcopy(item)
        item["effect"] = copy.deepcopy(item["base effect"])
        item["value"] = item["base value"]
        
        statNames = []
        if item["modifier"]["effect"] != []: statNames = [effect["type"] for effect in item["modifier"]["effect"] if effect["type"] in self.stats]
        if item["enchantments"] != []: statNames += [effect["type"] for effect in [enchantment["effect"] for enchantment in item["enchantments"]][0] if effect["type"] in self.stats]
        effects = []
        values = []
        
        values.append(item["modifier"]["value"])
        
        for effect in item["modifier"]["effect"]:
            if effect["type"] in self.stats: effects.append(effect)
        
        for enchantment in item["enchantments"]:
            values.append(enchantment["value"])
            for effect in enchantment["effect"]:
                if effect["type"] in self.stats: effects.append(effect)

        for value in values:
            if value[0] == "+": item["value"] += int(value[1:])
            elif value[0] == "-": item["value"] -= int(value[1:])
            elif value[0] == "*": item["value"] = round(float(value[1:]) * item["value"])

        for statName in statNames:
            for effect in item["effect"]:
                if statName == effect["type"]: statNames = [statName for statName in statNames if statName != effect["type"]]

        for e in effects:
            for effect in item["effect"]:
                if e["type"] == effect["type"]:
                    if effect["type"] == "attack":
                        for i in range(2):
                            if "*" in effect: effect["value"][i] *= (e["value"] + 1)
                            else: effect["value"][i] += e["value"]
                    else:
                        if "*" in effect: effect["value"] *= (e["value"] + 1)
                        else: effect["value"] += e["value"]
        return item

    def unequip(self, slot):
        self.addItem(self.equipment[slot])
        self.equipment[slot] = ""
        self.updateStats()

    def equip(self, item):
        if self.equipment[item["slot"]] != "": self.unequip(item["slot"])
        self.equipment[item["slot"]] = item
        self.removeItem(item)
        if item["slot"] == "tome": self.magic = item["effect"]
        self.updateEquipment(item["slot"])
        self.updateStats()

    def get_magic(self):
        magicSkill = copy.deepcopy(self.magic)
        for i in range(len(magicSkill)):
            if magicSkill[i]["type"] in ("all", "-all"):
                if type(magicSkill[i]["value"][0]) is list:
                    magicSkill[i]["value"][0] = [magicSkill[i]["value"][0][0] + self.stats["intelligence"], magicSkill[i]["value"][0][1] + self.stats["intelligence"]]
                else:
                    magicSkill[i]["value"][0] += self.__stats["intelligence"]
                if type(magicSkill[i]["value"][1]) is list:
                    magicSkill[i]["value"][1] = [magicSkill[i]["value"][1][0] + self.stats["intelligence"], magicSkill[i]["value"][1][1] + self.stats["intelligence"]]
                else:
                    magicSkill[i]["value"][1] += self.__stats["intelligence"]
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
        self.text = kwargs["text"]
        self.magic = kwargs.get("magic")
        self.tags = kwargs.get("tags")
        self.color = kwargs.get("color")
        self.levelDifference = 0
