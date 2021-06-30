import random
import math
import copy
from script.BaseClass import BaseClass
from script.Text import text
import script.Globals as Globals


class Entity(BaseClass):
    def __init__(self):
        self.defaultStats = {
            "attack": [1, 1],
            "armor": 0,
            "strength": 0,
            "intelligence": 0,
            "vitality": 0,
            "crit": 4,
            "hit": 90,
            "dodge": 5,
            "max hp": 7,
            "max mp": 10
        }
        
        for stat in self.defaultStats:
            if stat not in self.stats:
                self.stats[stat] = self.defaultStats[stat]
        
        self.baseStats = self.stats.copy()
        self.statChanges = dict((stat, [[0, 0], [0, 0], 0]) for stat in self.stats)

        self.equipment = {"": ""}
        self.passives = []
        self.guard = ""

    def update_stats(self):
        bufferhp = self.hp - self.stats["max hp"]
        buffermp = self.mp - self.stats["max mp"]
        oldMaxHp = self.stats["max hp"]
        oldMaxMp = self.stats["max mp"]
        effects = []
        self.statChanges = {statName: [[0, 0], [0, 0], -1] for statName in self.stats}
        
        if self.equipment["weapon"] == "":
            self.stats["attack"] = [1, 1]
        
        for slot in self.equipment:
            if self.equipment[slot] == "":
                continue
            
            effects += self.equipment[slot].effect
            if slot == "weapon":
                for effect in self.equipment["weapon"].effect:
                    if effect.type == "attack":
                        self.stats["attack"] = copy.deepcopy(effect.value)
        
        for passive in self.passives:
            if not type(passive["effect"]) is list:
                passive["effect"] = [passive["effect"]]
            effects += passive["effect"]
        
        for effect in effects:
            if effect.type not in self.stats or effect.type == "attack":
                continue
            if effect.opp == "=":
                self.statChanges[effect.type][2] = effect.value if effect.value < self.statChanges[effect.type][2] else self.statChanges[effect.type][2]
            elif effect.opp == "*":
                self.statChanges[effect.type][1][1] += effect.value
            else:
                self.statChanges[effect.type][1][0] += effect.value
        
        for statName in self.stats:
            if statName != "attack":
                self.stats[statName] = 0
                self.stats[statName] = self.baseStats[statName] + self.statChanges[statName][0][0] + self.statChanges[statName][1][0]
                self.stats[statName] += round(self.baseStats[statName] * (self.statChanges[statName][0][1] + self.statChanges[statName][1][1]) / 100)
                if self.statChanges[statName][0][1] + self.statChanges[statName][1][1] > 0 and self.stats[statName] == 0:
                    self.stats[statName] = 1
                if self.statChanges[statName][2] >= 0:
                    self.stats[statName] = self.statChanges[statName][2]
        
        self.__hp, self.__mp = self.stats["max hp"] + bufferhp, self.stats["max mp"] + buffermp
        if self.__hp <= 0 and bufferhp != 0 and self.stats["max hp"] - oldMaxHp != 0:
            self.__hp = 1
        if self.__mp <= 0 and buffermp != 0 and self.stats["max mp"] - oldMaxMp != 0:
            self.__mp = 0

    def defend(self, effect, attackerStats={}, tags=[], passive=False):
        effect = copy.deepcopy(effect)
        attackText = ""
        hpAmount = 0
        
        if "hit" not in attackerStats:
            attackerStats["hit"] = 95
        if "crit" not in attackerStats:
            attackerStats["crit"] = 4
        if "pierce" not in attackerStats:
            attackerStats["pierce"] = 1
        if "variance" not in attackerStats:
            attackerStats["variance"] = 20
        
        for i in range(len(tags)):
            tag = tags[i].split(":")
            if tag[0] in ("noMiss", "hit"):
                attackerStats["hit"] = 100
            elif tag[0] in ("noDodge", "hit"):
                attackerStats["dodge"] = 0
            elif tag[0] == "pierce":
                try:
                    attackerStats["pierce"] = 1 / float(tag[1])
                except ZeroDivisionError:
                    attackerStats["pierce"] = 0
            elif tag[0] == "variance":
                try:
                    attackerStats["variance"] = float(tag[1])
                except ZeroDivisionError:
                    attackerStats["variance"] = 20
        
        if effect.type in ("-hp", "-mp", "-all", "passive"):
            if effect.type != "passive":
                amount, a, r, v = [([0, 0] if effect.type == "-all" else 0) for i in range(4)]
                if effect.get("crit"):
                    crit = effect.crit
                elif attackerStats.get("crit"):
                    crit = attackerStats["crit"]
                else:
                    crit = 4

                critical = ''
                if random.randint(1, 100) <= crit:
                    crit = 2
                    critical = 'critical '

            if effect.get("hit"):
                h = effect.hit
            elif attackerStats.get("hit"):
                h = attackerStats["hit"]
            else:
                h = 95

            if effect.get("dodge"):
                d = effect.dodge
            elif attackerStats.get("dodge"):
                d = attackerStats["dodge"]
            else:
                d = 0

            if random.randint(1, 100) <= h:
                h = 1
            else:
                h = 0

            if random.randint(1, 100) <= d:
                d = 1
            else:
                d = 0

            if self.guard == "deflect":
                deflect = True
            else:
                deflect = False

            if self.guard == "block":
                return f'but {self.name} blocks the attack.', 0
            elif self.guard == "counter":
                return f'but {self.name} counters, ', 0
            elif not h:
                return 'but misses.', 0
            elif not d:
                return f'but {self.name} dodges.', 0

            if effect.type == "-all":
                if type(effect.value[0]) is list:
                    a[0] = random.randint(effect.value[0][0], effect.value[0][1])
                else:
                    a[0] = effect.value[0]
                if type(effect.value[1]) is list:
                    a[1] = random.randint(effect.value[1][0], effect.value[1][1])
                else:
                    a[1] = effect.value[1]
                r = (self.stats["armor"] / 2 + self.stats["vitality"]) * attackerStats["pierce"]
                v = [random.randint(100 - attackerStats["variance"], 100 + attackerStats["variance"]) / 100, random.randint(100 - attackerStats["variance"], 100 + attackerStats["variance"]) / 100]

                amount = [round((a[0] - r) * v[0] * crit), round((a[1] - r) * v[1] * crit)]
                if deflect:
                    amount = [round(amount[0] / 2), round(amount[1] / 2)]
                amount = [(1 if amount[0] < 1 else amount[0]), (1 if amount[1] < 1 else amount[1])]

                self.__hp -= amount[0]*h*d
                hpAmount = amount[0]*h*d*-1
                self.__mp -= amount[1]*h*d
                attackText = 'dealing {text.red}' + str(amount[0]) + ' ♥{reset} and {text.blue}' + str(amount[1]) + ' ♦{reset} ' + critical + 'damage'
            if effect.type in ("-hp", "-mp"):
                if type(effect.value) is list:
                    a = random.randint(effect.value[0], effect.value[1])
                else:
                    a = effect.value
                r = (self.stats["armor"] / 2 + self.stats["vitality"]) * attackerStats["pierce"]
                v = random.randint(100 - attackerStats["variance"], 100 + attackerStats["variance"]) / 100

                amount = round((a - r) * v * crit)
                if deflect:
                    amount = round(amount / 2)
                amount = 1 if amount < 1 else amount

                if effect.type == "-hp":
                    self.__hp -= amount*h*d
                    hpAmount = amount*h*d*-1
                    attackText = 'dealing {text.red}' + str(amount) + ' ♥{reset} ' + critical + 'damage'
                else:
                    self.__mp -= amount*h*d
                    attackText = 'dealing {text.blue}' + str(amount) + ' ♦{reset} ' + critical + 'damage'
            if effect.type == "passive":
                attackText = self.add_passive(effect)
        elif effect.type in ("hp", "mp", "all"):
            if effect.type == "all":
                if "*" in effect:
                    amount = [(effect.value[0] / 100) * self.stats["max hp"], (effect.value[1] / 100) * self.stats["max mp"]]
                else:
                    amount = [effect.value[0], effect.value[1]]
                amount = [1 if amount[0] < 1 else amount[0], 1 if amount[1] < 1 else amount[1]]
                if amount[0] + self.__hp > self.stats["max hp"]:
                    amount[0] = self.stats["max hp"] - self.__hp
                if amount[1] + self.__mp > self.stats["max mp"]:
                    amount[1] = self.stats["max mp"] - self.__mp

                self.__hp += amount[0]
                hpAmount = amount[0]
                self.__mp += amount[1]
                attackText = 'healing {text.red}{amount[0]} ♥{reset} and {text.blue}{amount[1]} ♦{reset}'
            else:
                if "*" in effect:
                    amount = (effect.value / 100) * self.stats["max hp"]
                else:
                    amount = effect.value
                if amount < 1:
                    amount = 1

                if effect.type == "hp":
                    if amount + self.__hp > self.stats["max hp"]:
                        amount = self.stats["max hp"] - self.__hp
                    self.__hp += amount
                    hpAmount = amount
                    attackText = 'healing {text.red}' + str(amount) + ' ♥{reset}'
                else:
                    if amount + self.__mp > self.stats["max mp"]:
                        amount = self.stats["max mp"] - self.__mp
                    self.__mp += amount
                    attackText = 'healing {text.blue}' + str(amount) + ' ♦{reset}'
        elif effect.type == "stat":
            if "*" in effect:
                self.baseStats[effect.stat] = round(self.baseStats[effect.stat] * ((effect.value + 1) / 100))
            else:
                self.baseStats[effect.stat] += effect.value
            self.update_stats()
            color = ""
            symbol = ""
            if effect.stat == "max hp":
                color = '{text.red}'
                symbol = " ♥"
            if effect.stat == "max mp":
                color = '{text.blue}'
                symbol = " ♦"
            return 'increasing ' + effect.stat.title() + ' by ' + color + str(effect.value) + '{reset}' + ("%" if "*" in effect else "") + color + symbol + '{reset}.', 0
        if passive:
            if type(passive) is list:
                for i in range(len(passive)):
                    attackText += ", "
                    if i == len(passive) - 1:
                        attackText += "and "
                    attackText += self.add_passive(passive[i])
            else:
                attackText += " and "
                attackText += self.add_passive(passive)
        else:
            attackText += "."
        return attackText, hpAmount

    def add_passive(self, passive):
        passive.update({"dodge": 0, "hit": 100})
        passiveFound = False
        if type(passive["turns"]) is list:
            turns = random.randint(passive["turns"][0], passive["turns"][1])
        else:
            turns = passive["turns"]
        passive["turns"] = turns
        for p in self.passives:
            if passive["name"] == p["name"]:
                passiveFound = True
                p["turns"] = turns
                break
        if not passiveFound:
            self.passives.append(passive)
        self.update_stats()
        return f'applying {text.c("light green" if passive["buff"] == True else "light red")}{passive["name"]}{text.reset} ({passive["turns"]})'

    def update(self):
        self.update_stats()
        attackText = []
        for passive in self.passives:
            for effect in passive["effect"]:
                if effect.type in ("-hp", "-mp", "-all", "hp", "mp", "all"):
                    prefix = f' {text.c("light green" if passive["buff"] else "light red")}{passive["name"]}{text.reset} persists, '
                    suffix, tempDamage = self.defend(effect)
                    attackText.append(prefix + suffix)
            
            passive["turns"] -= 1
            if passive["turns"] <= 0:
                self.passives.remove(passive)
                attackText.append(f' {passive["name"]} wears off.')
                continue
        return attackText, tempDamage

    def attack(self):
        attackSkill = {"type": "-hp", "value": [self.stats["attack"][0] + self.stats["strength"], self.stats["attack"][1] + self.stats["strength"]], "crit": self.stats["crit"], "hit": self.stats["hit"]}
        if "weapon" in self.equipment and self.equipment["weapon"] != "":
            passives = []
            for effect in self.equipment["weapon"]["effect"]:
                if effect.type == "passive":
                    passives.append(effect.value)
                if "passive" in effect:
                    passives += effect.passive
            attackSkill.update({"passive": passives})
        return attackSkill
    
    def show_passives(self):
        if len(self.passives) > 0:
            print(" ", end="")
            print(", ".join([f'{text.c("light green" if passive["buff"] else "light red")}{passive["name"]}{text.reset} ({passive["turns"]})' for passive in self.passives]))


class Player(Entity):
    def __init__(self, equipment, mainQuests):
        self.hp = 7
        self.mp = 10
        self.level = 1
        self.name = "Name"
        self.stats = {}
        
        super().__init__()
        
        self.__xp, self.mxp, self.gold = 0, 10, 0
        self.levelsGained = 0
        self.saveId = random.randint(1000, 9999)
        
        self.location = "fordsville"
        self.x = 799
        self.y = 690
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
        
        self.update_stats()
    
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
            self.update_stats()
            self.__hp = self.stats["max hp"]
            self.__mp = self.stats["max mp"]
            self.level += 1
            self.levelsGained += self.level % 2
            
    xp = property(getXp, setXp)

    def addQuest(self, quest):
        for i in range(len(quest["objective"])):
            quest["objective"][i].update({"status": 0, "complete": False})
        if "location" not in quest:
            quest["location"] = None
        elif len(quest["location"]) == 2:
            self.locations[quest["location"][0]].append(quest["location"][1])
        self.quests.append(quest)

    def updateQuests(self, enemy=None, item=None, location=None):
        for i in range(len(self.quests)):
            complete = True
            for j in range(len(self.quests[i]["objective"])):
                if self.quests[i]["objective"][j]["type"] == "kill":
                    if enemy and enemy.name == self.quests[i]["objective"][j]["name"]:
                        self.quests[i]["objective"][j]["status"] += 1
                        if self.quests[i]["objective"][j]["status"] >= self.quests[i]["objective"][j]["quantity"]:
                            self.quests[i]["objective"][j]["complete"] = True
                elif self.quests[i]["objective"][j]["type"] == "obtain":
                    if item and item[0].name == self.quests[i]["objective"][j]["name"]:
                        self.quests[i]["objective"][j]["status"] += item[1]
                        if self.quests[i]["objective"][j]["status"] >= self.quests[i]["objective"][j]["quantity"]:
                            self.quests[i]["objective"][j]["complete"] = True
                if not self.quests[i]["objective"][j]["complete"]:
                    complete = False
            if complete:
                self.completedQuests.append(self.quests[i])
                self.finishQuest(i)
    
    def finishQuest(self, index):
        quest = self.quests.pop(index)
        if quest.get("main") and self.mainQuest + 1 < len(self.mainQuests):
            self.mainQuest += 1
            self.addQuest(self.mainQuests[self.mainQuest])
        if "item" in quest["reward"]:
            for item in quest["reward"]["item"]:
                self.add_item(item[0], item[1])
        if "xp" in quest["reward"]:
            self.xp += quest["reward"]["xp"]
        if "gold" in quest["reward"]:
            self.gold += quest["reward"]["gold"]
        if "stat" in quest["reward"]:
            for stat in quest["reward"]["stat"]:
                if stat.get("*"):
                    self.baseStats[stat["type"]] = round(self.baseStats[stat["type"]] * (1 + stat["value"]))
                else:
                    self.baseStats[stat["type"]] += stat["value"]

    def num_of_items(self, name):
        num = 0
        for item in self.inventory:
            if item[0].name == name:
                num += item[1]
        return num

    def add_item(self, item, quantity=1):
        if not item:
            return
        self.updateQuests(item=[item, quantity])
        if item.type in Globals.stackableItems:
            for i in self.inventory:
                if i[0].name == item.name:
                    i[1] += quantity
                    return
            self.inventory.append([item, quantity])
            return
        else:
            for i in range(quantity):
                self.inventory.append([item, 1])
            return

    def remove_item(self, item, quantity=1):
        if item.type in Globals.stackableItems:
            for i in self.inventory:
                if i[0].name == item.name:
                    i[1] -= quantity
                    if i[1] <= 0:
                        self.inventory.remove([i[0], i[1]])
                    return
        else:
            for i in range(quantity):
                if [item, 1] in self.inventory:
                    self.inventory.remove([item, 1])
            return
    
    def unequip(self, slot):
        self.add_item(self.equipment[slot])
        self.equipment[slot] = ""
        self.update_stats()

    def equip(self, item):
        if self.equipment[item.slot] != "":
            self.unequip(item.slot)
        self.equipment[item.slot] = item
        self.remove_item(item)
        if item.slot == "tome":
            self.magic = item.effect
        self.update_stats()

    def get_magic(self):
        magicSkill = copy.deepcopy(self.magic)
        for i in range(len(magicSkill)):
            if magicSkill[i]["type"] in ("all", "-all"):
                if type(magicSkill[i]["value"][0]) is list:
                    magicSkill[i]["value"][0] = [magicSkill[i]["value"][0][0] + self.stats["intelligence"], magicSkill[i]["value"][0][1] + self.stats["intelligence"]]
                else:
                    magicSkill[i]["value"][0] += self.stats["intelligence"]
                if type(magicSkill[i]["value"][1]) is list:
                    magicSkill[i]["value"][1] = [magicSkill[i]["value"][1][0] + self.stats["intelligence"], magicSkill[i]["value"][1][1] + self.stats["intelligence"]]
                else:
                    magicSkill[i]["value"][1] += self.stats["intelligence"]
            else:
                if type(magicSkill[i]["value"]) is list:
                    magicSkill[i]["value"] = [magicSkill[i]["value"][0] + self.stats["intelligence"], magicSkill[i]["value"][1] + self.stats["intelligence"]]
                else:
                    magicSkill[i]["value"] += self.stats["intelligence"]
        return magicSkill
    
    def show_stats(self, passives=True):
        print("")
        print("", text.title(self.name, self.level))
        print("", text.hp, text.bar(self.hp, self.stats["max hp"], "red", number=True))
        print("", text.mp, text.bar(self.mp, self.stats["max mp"], "blue", number=True))
        print("", text.xp, text.bar(self.xp, self.mxp, "green", number=True))
        print("", text.gp, text.reset + str(self.gold))
        if passives: self.show_passives()


class Enemy(Entity):
    def __init__(self, attributes):
        self.defaults = {
            "hp": 7,
            "mp": 5,
            "stats": {},
            "level": [1,1],
            "gold": 1,
            "xp": 1,
            "text": "attacks",
            "tags": {},
            "magic": [],
            "levelDifference": 0
        }
        
        super().super().__init__(attributes, self.defaults)
        super().__init__()
        
        self.update_stats()
