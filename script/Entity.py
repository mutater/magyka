import copy
import json
import math
import random
from script.BaseClass import BaseClass
from script.Control import control
from script.Effect import Effect, Passive
from script.Logger import logger
from script.Text import text
import script.Globals as Globals


class Entity(BaseClass):
    def __init__(self, attributes, defaults):
        self.defaults = {
            "name": "Name",
            "equipment": {
                "weapon": "",
                "tome": "",
                "head": "",
                "chest": "",
                "legs": "",
                "acc 1": "",
                "acc 2": ""
            },
            "passives": [],
            "stats": {},
            "baseStats": {},
            "statChanges": {},
            "tags": {}
        }
        
        self.defaults.update(defaults)
        
        super().__init__(attributes, self.defaults)
        
        self.defaultStats = {
            "attack": [1, 1],
            "armor": 0,
            "strength": 0,
            "intelligence": 0,
            "vitality": 0,
            "crit": 4,
            "hit": 90,
            "dodge": 3,
            "max hp": 7,
            "max mp": 10
        }
        
        for stat in self.defaultStats:
            if stat not in self.stats:
                self.stats[stat] = self.defaultStats[stat]
        
        self.baseStats = self.stats.copy()
        self.statChanges = dict((stat, [[0, 0], [0, 0], 0]) for stat in self.stats)

        self.guard = ""

    def update_stats(self):
        bufferhp = self.hp - self.stats["max hp"]
        buffermp = self.mp - self.stats["max mp"]
        oldMaxHp = self.stats["max hp"]
        oldMaxMp = self.stats["max mp"]
        effects = []
        self.statChanges = {statName: [[0, 0], [0, 0], -1] for statName in self.stats}
        self.tags = {}
        
        if not self.equipment.get("weapon"):
            self.stats["attack"] = self.baseStats["attack"].copy()
        
        for slot in self.equipment:
            if self.equipment[slot] == "":
                continue
            
            effects += self.equipment[slot].effect
            if slot == "weapon":
                for effect in self.equipment["weapon"].effect:
                    if effect.type == "attack":
                        self.stats["attack"] = copy.deepcopy(effect.value)
        
        for passive in self.passives:
            effects += passive.effect
        
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

    def defend(self, effect, attackerStats={}, tags={}, passive=False):
        if passive:
            print("")
            text.slide_cursor(0, 4)
            print("and ", end="")
            for i in range(len(effect)):
                if i > 0:
                    print(", ", end="")
                    if i < len(effect):
                        print("and ", end="")
                self.add_passive(effect[i])
            print(".")
            return
        
        attackerStats = copy.deepcopy(attackerStats)
        tags = copy.deepcopy(tags)
        
        if "hit" not in attackerStats:
            attackerStats["hit"] = 90
        if "crit" not in attackerStats:
            attackerStats["crit"] = 4
        
        if "pierce" in tags:
            attackerStats["pierce"] = tags["pierce"] / 100
        else:
            attackerStats["pierce"] = 0
        if "variance" in tags:
            attackerStats["variance"] = tags["variance"]
        else:
            attackerStats["variance"] = 20
        
        if effect.type in ("damageHp", "damageMp", "passive"):
            if effect.type != "passive":
                amount, a, r, v = 0, 0, 0, 0
                crit = 0
                if attackerStats.get("crit"):
                    crit = attackerStats.get("crit")
                crit += effect.crit

                critical = ''
                if random.randint(1, 100) <= crit:
                    crit = 2
                    critical = 'critical '
                else:
                    crit = 1
            
            deflect = self.guard == "deflect"

            if self.guard == "block":
                print(f'but {self.name} blocks the attack.')
                return
            elif self.guard == "counter":
                return

            if effect.type in ("damageHp", "damageMp"):
                if type(effect.value) is list:
                    a = random.randint(round(effect.value[0]), round(effect.value[1]))
                else:
                    a = effect.value
                r = (self.stats["armor"] - (self.stats["armor"] * attackerStats["pierce"]) / 2 + self.stats["vitality"] / 2)
                if attackerStats["variance"] != 0:
                    v = random.randint(100 - attackerStats["variance"], 100 + attackerStats["variance"]) / 100
                else:
                    v = 1
                
                amount = round((a - r) * v * crit)
                if deflect:
                    amount //= 2
                amount = 1 if amount < 1 else amount

                if effect.type == "damageHp":
                    self.hp -= amount
                    print(f'dealing {amount} {text.hp}{text.reset} {critical}damage', end="")
                else:
                    self.mp -= amount
                    print(f'dealing {amount} {text.mp}{text.reset} {critical}damage', end="")
            elif effect.type == "passive":
                self.add_passive(effect)
        elif effect.type in ("healHp", "healMp"):
            if type(effect.value) is list:
                amount = random.randint(effect.value[0], effect.value[1])
            
            if effect.opp == "*":
                if effec.type == "healHp":
                    amount = (amount / 100) * self.stats["max hp"]
                else:
                    amount = (amount / 100) * self.stats["max mp"]
            
            amount += self.stats["vitality"] / 2
            amount = max(round(amount), 1)

            if effect.type == "healHp":
                if amount + self.hp > self.stats["max hp"]:
                    amount = self.stats["max hp"] - self.hp
                self.hp += amount
                print(f'healing {amount} {text.hp}{text.reset}', end="")
            else:
                if amount + self.mp > self.stats["max mp"]:
                    amount = self.stats["max mp"] - self.mp
                self.mp += amount
                print(f'healing {amount} {text.mp}{text.reset}', end="")
        elif effect.type == "stat":
            if effect.opp == "*":
                self.baseStats[effect.stat] = round(self.baseStats[effect.stat] * ((effect.value + 1) / 100))
            else:
                self.baseStats[effect.stat] += effect.value
            self.update_stats()

            if effect.stat == "max hp":
                symbol = text.hp
            if effect.stat == "max mp":
                symbol = text.mp
            else:
                symbol = ""
            
            if (effect.opp == "*" and effect.value >= 1) or (effect.opp != "*" and effect.opp > 0):
                increase = "increasing"
            else:
                increase = "decreasing"
            
            print(f'{increase} {effect.stat.title()} by {str(effect.value)}{"%" if "*" in effect else ""}{text.reset}', end="")
        
        if effect.passive:
            self.defend(effect.passive, passive=True)
        
        if self.hp < 0:
            self.hp = 0
        if self.hp >= self.stats["max hp"]:
            self.hp = self.stats["max hp"]
        if self.mp < 0:
            self.mp = 0
        if self.mp >= self.stats["max mp"]:
            self.mp = self.stats["max mp"]

    def add_passive(self, passive):
        if not passive:
            return
        passive = copy.deepcopy(passive)
        passive.dodge = 0
        passive.hit = 100
        passiveFound = False
        if type(passive.turns) is list:
            turns = random.randint(passive.turns[0], passive.turns[1])
        else:
            turns = passive.turns
        passive.turns = turns
        
        for p in self.passives:
            if passive.name == p.name:
                passiveFound = True
                p.turns = turns
                break
        if not passiveFound:
            self.passives.append(passive)
        self.update_stats()
        print(f'applying {passive.get_name(turns=True)}', end="")

    def update(self):
        self.update_stats()
        attackText = []
        for passive in self.passives:
            for effect in passive.effect:
                if effect.type in ("damageHp", "damageMp", "healHp", "healMp"):
                    text.slide_cursor(1, 3)
                    print(f'{passive.get_name()} persists, ', end="")
                    self.defend(effect)
            
            passive.turns -= 1
            if passive.turns <= 0:
                self.passives.remove(passive)
                text.slide_cursor(1, 3)
                print(f'{passive.get_name()} wears off.')
                continue

    def attack(self, entity, type="attack", message=True):
        attackText = ""
        attack = None
        if type == "attack":
            if hasattr(self, "text"):
                attackText = f'{self.name} {self.text} {entity.name}, '
            else:
                if self.equipment.get("weapon"):
                    attackText = f'{self.name} {self.equipment["weapon"].text} {entity.name}, '
                else:
                    attackText = f'{self.name} attacks {entity.name}, '
            attack = self.get_attack()
        elif type == "magic":
            attackText = "magics"
            attack = self.get_magic()
            if self.equipment["tome"].target == "self":
                attackText = f'{self.name} casts {self.equipment["tome"].text}, '
            else:
                attackText = f'{self.name} casts {self.equipment["tome"].text} on {entity.name}, '
        
        if message:
            text.slide_cursor(1, 3)
            print(attackText, end="")
        
        if random.randint(1, 100) > self.stats["hit"]:
            print("but misses.")
            return
        elif random.randint(1, 100) <= entity.stats["dodge"]:
            print(f'but {entity.name} dodges.')
            return
        
        for i in range(len(attack)):
            entity.defend(attack[i])
            if len(attack) > 2:
                print(", ", end="")
            if i < len(attack) - 1:
                print(" and")
                text.slide_cursor(0, 4)
        print(".")

    def get_attack(self):
        attackSkill = {"type": "damageHp", "value": [self.stats["attack"][0]+self.stats["strength"]/2, self.stats["attack"][1]+self.stats["strength"]/2],\
        "crit": self.stats["crit"], "hit": self.stats["hit"], "tags": {}}
        if self.equipment.get("weapon"):
            passives = []
            for effect in self.equipment["weapon"].effect:
                if effect.type == "passive":
                    passives += effect.value
                if effect.passive:
                    passives += effect.passive
            attackSkill.update({"passive": passives})
        if self.equipment:
            for slot in self.equipment:
                if slot == "weapon" or not self.equipment[slot]:
                    continue
                if self.equipment[slot].tags:
                    for tag, value in self.equipment[slot].tags.items():
                        if tag in ("variance", "pierce", "passive"):
                            attackSkill[tag] = copy.deepcopy(value)
        return [Effect(attackSkill)]
    
    def get_magic(self):
        magicSkill = copy.deepcopy(self.magic)
        """
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
        """
        return magicSkill
    
    def show_passives(self):
        if len(self.passives) > 0:
            text.slide_cursor(0, 3)
            print(", ".join([f'{passive.get_name(turns=True)}' for passive in self.passives]))
    
    def show_stats(self, gpxp=True, passives=True, small=False):
        if small:
            barLength = 16
        else:
            barLength = 40
        print("")
        text.slide_cursor(1, 3)
        print(text.title(self.name, self.level, self.playerClass if hasattr(self, "playerClass") else ""))
        text.slide_cursor(0, 3)
        print(text.hp, text.bar(self.hp, self.stats["max hp"], "red", length=barLength, number=True))
        text.slide_cursor(0, 3)
        print(text.mp, text.bar(self.mp, self.stats["max mp"], "blue", length=barLength, number=True))
        if gpxp:
            text.slide_cursor(0, 3)
            print(text.xp, text.bar(self.xp, self.mxp, "green", length=barLength, number=True))
            text.slide_cursor(0, 3)
            print(text.gp, text.reset + str(self.gold))
        if passives: self.show_passives()
    

class Player(Entity, BaseClass):
    def __init__(self, attributes):
        self.defaults = {
            "table": "player",
            "hp": 7,
            "mp": 10,
            "level": 1,
            "extraStats": {},
            "location": "magyka",
            "x": 128,
            "y": 113,
            "saveId": random.randint(10000, 99999),
            "quests": [],
            "mainQuests": [],
            "levelsGained": 0,
            "mainQuest": 0,
            "completedQuests": [],
            "inventory": [],
            "magic": None,
            "xp": 0,
            "mxp": 10,
            "gold": 0,
            "playerClass": "class"
        }
        
        super().__init__(attributes, self.defaults)
        
        for quest in self.mainQuests:
            quest.update({"main": True})
        self.addQuest(self.mainQuests[0])
        
        self.update_stats()

    def level_up(self):
        while self.xp >= self.mxp:
            self.xp -= self.mxp
            self.mxp = math.ceil(self.mxp * 1.2)
            self.level += 1
            self.levelsGained += 1
            
            self.baseStats["max hp"] += self.extraStats["hpPerLevel"]
            self.baseStats["max mp"] += self.extraStats["mpPerLevel"]
            if self.level % 3 == 0:
                self.baseStats["strength"] += self.extraStats["strengthPerLevel"]
                self.baseStats["vitality"] += self.extraStats["vitalityPerLevel"]
                self.baseStats["intelligence"] += self.extraStats["intelligencePerLevel"]
            self.update_stats()
            
            self.hp = self.stats["max hp"]
            self.mp = self.stats["max mp"]

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
        if not item:
            return
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
        if not item:
            return
        if item.slot == "accessory":
            if not self.equipment.get("acc 1"):
                slot = "acc 1"
            else:
                slot = "acc 2"
        else:
            slot = item.slot
        if self.equipment.get(slot):
            self.unequip(slot)
        self.equipment[slot] = item
        self.remove_item(item)
        if item.slot == "tome":
            self.magic = item.effect
        self.update_stats()
    
    def export(self):
        for i in range(len(self.inventory)):
            self.inventory[i][0] = self.inventory[i][0].export()
        for i in range(len(self.passives)):
            self.passives[i] = self.passives[i].export()
        for slot in self.equipment:
            if self.equipment[slot]:
                self.equipment[slot] = self.equipment[slot].export()
        if self.magic:
            self.magic = self.magic.export()
        return json.dumps(super().export())


class Enemy(Entity):
    def __init__(self, attributes):
        self.defaults = {
            "table": "enemies",
            "hp": 7,
            "mp": 5,
            "stats": {},
            "level": [1,1],
            "gold": 1,
            "xp": 1,
            "text": "attacks",
            "magic": [],
            "levelDifference": 0
        }
        
        attributes["stats"]["max hp"] = attributes.get("hp", self.defaults["hp"])
        attributes["stats"]["max mp"] = attributes.get("mp", self.defaults["mp"])
        
        super().__init__(attributes, self.defaults)
        
        self.update_stats()
