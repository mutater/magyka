import copy
import math
import random
from script.Effect import Effect
from script.Logger import logger
from script.Text import text
import script.Globals as Globals


class Entity:
    """
    Holds the data for an entity, whether it be a player or an enemy.
    """

    def __init__(self, attributes):
        """
        Load the entity's attributes and set up baseStats and statChanges.

        Args:
            attributes:
                name:
                    String display name.
                class:
                    String class.
                text:
                    String text shown when attacking without a weapon equipped.
                equipment:
                    Dict of slot: Item (the items equipped). See Globals.slotList.
                inventory:
                    List of items the entity has.

                    Each item is in the format [Item, quantity].
                passives:
                    List of Passives applied.
                stats:
                    Dict of Entity stats (hp, attack, etc.). See Globals.statList.
                extraStats:
                    Dict of any extra stats not in Globals.statList.
                hp:
                    Integer health points.
                mp:
                    Integer magic points.
                gold:
                    Integer gold quantity.
                xp:
                    Integer xp quantity.
                mxp:
                    Integer xp needed to level up.
                level:
                    Integer or 2 length List of Integers.
                baseStats:
                    Dict base stats of the entity without regards to equipment, passives, or others.
                defaultStats:
                    Dict default stats of an entity
                tags:
                    Dict of any extra information.

        Attrs:
            statChanges:
                Dict difference between stats and baseStats.
            guard:
                String guard state ("deflect", "block", or "counter").
        """

        self.attributes = {
            "name": "Name",
            "class": "Warrior",
            "text": "attacks",
            "equipment": {
                "weapon": "",
                "tome": "",
                "head": "",
                "chest": "",
                "legs": "",
                "acc 1": "",
                "acc 2": ""
            },
            "inventory": [],
            "passives": [],
            "stats": {},
            "extraStats": {},
            "baseStats": {},
            "statChanges": {},
            "hp": 7,
            "mp": 10,
            "gold": 0,
            "xp": 0,
            "mxp": 10,
            "level": 1,
            "tags": {}
        }
        self.attributes.update(attributes)

        if "max hp" not in self.attributes["stats"]:
            self.attributes["stats"]["max hp"] = self.attributes["hp"]

        if "max mp" not in self.attributes["stats"]:
            self.attributes["stats"]["max mp"] = self.attributes["mp"]

        self.attributes.update({"defaultStats": {
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
        }})

        for stat in self.attributes["defaultStats"]:
            if stat not in self.attributes["stats"]:
                self.attributes["stats"][stat] = self.attributes["defaultStats"][stat]

        baseStats = self.attributes["stats"].copy()
        self.attributes.update({"baseStats": baseStats})
        self.attributes["statChanges"] = dict((stat, {"+": 0, "*": 1, "=": 0}) for stat in self.attributes["stats"])
        self.guard = ""

    def update_stats(self):
        """
        Updates the Entity stats based on equipment, current passives, etc.
        """

        effects = []
        self.attributes["statChanges"] = dict((stat, {"+": 0, "*": 100, "=": -1}) for stat in self.attributes["stats"])

        # Replace attack if no weapon equipped.
        if not self.attributes["equipment"].get("weapon"):
            self.attributes["stats"]["attack"] = self.attributes["baseStats"]["attack"].copy()

        # Get the effects of the equipment.
        for slot in self.attributes["equipment"]:
            if self.attributes["equipment"][slot] == "":
                continue

            effects += self.attributes["equipment"][slot].attributes["effect"]
            if slot == "weapon":
                for effect in self.attributes["equipment"]["weapon"].attributes["effect"]:
                    if effect.attributes["type"] == "attack":
                        self.attributes["stats"]["attack"] = copy.deepcopy(effect.attributes["value"])

        # Get the effects of the passives
        for passive in self.attributes["passives"]:
            effects += passive.attributes["effect"]

        # Get the stat changes of the effects
        for effect in effects:
            if effect.attributes["type"] not in self.attributes["stats"] or effect.attributes["type"] == "attack":
                continue

            if effect.attributes["opp"] == "=":
                if effect.attributes["value"] < self.attributes["statChanges"][effect.attributes["type"]]["="]:
                    self.attributes["statChanges"][effect.attributes["type"]]["="] = effect.attributes["value"]
                else:
                    self.attributes["statChanges"][effect.attributes["type"]]["="] = self.attributes["statChanges"][effect.attributes["type"]]["="]
            elif effect.attributes["opp"] == "*":
                self.attributes["statChanges"][effect.attributes["type"]]["*"] += effect.attributes["value"]
            else:
                self.attributes["statChanges"][effect.attributes["type"]]["+"] += effect.attributes["value"]

        # Apply statChanges to stats
        for statName in self.attributes["stats"]:
            if statName == "attack":
                continue

            self.attributes["stats"][statName] = (
                self.attributes["statChanges"][statName]["+"] +
                round(self.attributes["baseStats"][statName] * self.attributes["statChanges"][statName]["*"] / 100)
            )

            # if self.attributes["statChanges"][statName][0][1] + self.attributes["statChanges"][statName][1][1] > 0\
            #         and self.attributes["stats"][statName] == 0:
            #     self.attributes["stats"][statName] = 1
            if self.attributes["statChanges"][statName]["="] >= 0:
                self.attributes["stats"][statName] = self.attributes["statChanges"][statName][2]

        if self.attributes["hp"] > self.attributes["stats"]["max hp"]:
            self.attributes["hp"] = self.attributes["stats"]["max hp"]

    def defend(self, effect, attackerStats={}, tags={}, passive=False):
        """
        Defend or receive an Effect.

        Args:
            effect:
                Effect.
            attackerStats:
                Dict of stats of the attacker.
            tags:
                Tags of the attacker, whether it be the Entity, Effect, Item, or Passive.
            passive:
                Boolean; if True, the effect param is applied as a passive instantly. Default is False.

        Returns:

        """

        logger.log(effect, effect.attributes["type"], effect.attributes["value"])

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

        if effect.attributes["type"] in ("-hp", "-mp", "passive"):
            deflect = self.guard == "deflect"

            if self.guard == "block":
                print(f'but {self.attributes["name"]} blocks the attack.')
                return
            elif self.guard == "counter":
                return

            if effect.attributes["type"] in ("-hp", "-mp"):
                crit = 0
                if attackerStats.get("crit"):
                    crit = attackerStats.get("crit")
                crit += effect.attributes["crit"]

                critical = ''
                if random.randint(1, 100) <= crit:
                    crit = 2
                    critical = 'critical '
                else:
                    crit = 1

                if type(effect.attributes["value"]) is list:
                    a = random.randint(round(effect.attributes["value"][0]), round(effect.attributes["value"][1]))
                else:
                    a = effect.attributes["value"]

                r = (self.attributes["stats"]["armor"]
                     - (self.attributes["stats"]["armor"] * attackerStats["pierce"]) / 2
                     + self.attributes["stats"]["vitality"] / 2)

                if attackerStats["variance"] != 0:
                    v = random.randint(100 - attackerStats["variance"], 100 + attackerStats["variance"]) / 100
                else:
                    v = 1

                amount = round((a - r) * v * crit)
                if deflect:
                    amount //= 2
                amount = max(1, amount)

                if effect.attributes["type"] == "-hp":
                    self.attributes["hp"] -= amount
                    print(f'dealing {amount} {text.hp}{text.reset} {critical}damage', end="")
                else:
                    self.attributes["mp"] -= amount
                    print(f'dealing {amount} {text.mp}{text.reset} {critical}damage', end="")
            elif effect.attributes["type"] == "passive":
                self.add_passive(effect)
        elif effect.attributes["type"] in ("+hp", "+mp"):
            if type(effect.attributes["value"]) is list:
                amount = random.randint(effect.attributes["value"][0], effect.attributes["value"][1])
            else:
                amount = effect.attributes["value"]

            if effect.attributes["opp"] == "*":
                if effect.attributes["type"] == "+hp":
                    amount = (amount / 100) * self.attributes["stats"]["max hp"]
                else:
                    amount = (amount / 100) * self.attributes["stats"]["max mp"]

            amount += self.attributes["stats"]["vitality"] / 2
            amount = max(round(amount), 1)

            if effect.attributes["type"] == "+hp":
                if amount + self.attributes["hp"] > self.attributes["stats"]["max hp"]:
                    amount = self.attributes["stats"]["max hp"] - self.attributes["hp"]
                self.attributes["hp"] += amount
                print(f'healing {amount} {text.hp}{text.reset}', end="")
            else:
                if amount + self.attributes["mp"] > self.attributes["stats"]["max mp"]:
                    amount = self.attributes["stats"]["max mp"] - self.attributes["mp"]
                self.attributes["mp"] += amount
                print(f'healing {amount} {text.mp}{text.reset}', end="")
        elif effect.attributes["type"] == "stat":
            if effect.attributes["opp"] == "*":
                self.attributes["baseStats"][effect.attributes["stat"]] = round(
                    self.attributes["baseStats"][effect.attributes["stat"]] * ((effect.attributes["value"] + 1) / 100))
            else:
                self.attributes["baseStats"][effect.attributes["stat"]] += effect.attributes["value"]
            self.update_stats()

            if effect.stat == "max hp":
                symbol = " " + text.hp
            elif effect.stat == "max mp":
                symbol = " " + text.mp
            else:
                symbol = ""

            if (effect.opp == "*" and effect.attributes["value"] >= 1) or (effect.opp != "*" and effect.opp > 0):
                increase = "increasing"
            else:
                increase = "decreasing"

            percent = "%" if "*" in effect else ""

            print(f'{increase} {effect.stat.title()}{symbol} by {str(effect.attributes["value"])}{percent}{text.reset}', end="")

        if effect.attributes["passive"]:
            self.defend(effect.attributes["passive"], passive=True)

        if self.attributes["hp"] < 0:
            self.attributes["hp"] = 0
        if self.attributes["hp"] >= self.attributes["stats"]["max hp"]:
            self.attributes["hp"] = self.attributes["stats"]["max hp"]
        if self.attributes["mp"] < 0:
            self.attributes["mp"] = 0
        if self.attributes["mp"] >= self.attributes["stats"]["max mp"]:
            self.attributes["mp"] = self.attributes["stats"]["max mp"]

    def add_passive(self, passive):
        """
        Adds a passive to the Entity and formats it.

        Args:
            passive:
                Passive added to the Entity.
        """
        if not passive:
            return

        passive = copy.deepcopy(passive)
        passive.dodge = 0
        passive.hit = 100
        passiveFound = False

        if type(passive.attributes["turns"]) is list:
            turns = random.randint(passive.attributes["turns"][0], passive.attributes["turns"][1])
        else:
            turns = passive.attributes["turns"]

        passive.attributes["turns"] = turns

        for p in self.attributes["passives"]:
            if passive.name == p.name:
                passiveFound = True
                p.attributes["turns"] = turns
                break
        if not passiveFound:
            self.attributes["passives"].append(passive)
        self.update_stats()
        print(f'applying {passive.get_name(turns=True)}', end="")

    def update(self):
        self.update_stats()
        for passive in self.attributes["passives"]:
            for effect in passive.attributes["effect"]:
                if effect.attributes["type"] in ("-hp", "-mp", "+hp", "+mp"):
                    text.slide_cursor(1, 3)
                    print(f'{passive.get_name()} persists, ', end="")
                    self.defend(effect)

            passive.attributes["turns"] -= 1
            if passive.attributes["turns"] <= 0:
                self.attributes["passives"].remove(passive)
                text.slide_cursor(1, 3)
                print(f'{passive.get_name()} wears off.')
                continue

    def attack(self, entity, type="attack", message=True):
        """
        Attacks a target Entity.

        Args:
            entity:
                Entity target.
            type:
                String type of attack ("attack", "magic").
            message:
                Boolean; if True, show the attack message. Default is true.
        """

        attackText = ""
        attack = None

        if type == "attack":
            if "text" in self.attributes:
                attackText = f'{self.attributes["name"]} {self.attributes["text"]} {entity.attributes["name"]}, '
            else:
                if self.attributes["equipment"].get("weapon"):
                    attackText = (
                        f'{self.attributes["name"]}'
                        + f'{self.attributes["equipment"]["weapon"].attributes["text"]}'
                        + f'{entity.attributes["name"]}, ')
                else:
                    attackText = f'{self.attributes["name"]} attacks {entity.name}, '
            attack = self.get_attack()

        if message:
            text.slide_cursor(1, 3)
            print(attackText, end="")

        if random.randint(1, 100) > self.attributes["stats"]["hit"]:
            print("but misses.")
            return
        elif random.randint(1, 100) <= entity.attributes["stats"]["dodge"]:
            print(f'but {entity.attributes["name"]} dodges.')
            return

        for i in range(len(attack)):
            entity.defend(attack[i], tags=self.attributes["tags"])
            if len(attack) > 2:
                print(", ", end="")
            if i < len(attack) - 1:
                print(" and")
                text.slide_cursor(0, 4)
        print(".")

    def get_attack(self):
        """
        Gets and formats the base attack of the Entity.

        Returns:
            List of Effect.
        """

        attackSkill = {
            "type": "-hp",
            "value": [
                self.attributes["stats"]["attack"][0] + self.attributes["stats"]["strength"] / 2,
                self.attributes["stats"]["attack"][1] + self.attributes["stats"]["strength"] / 2
            ],
            "crit": self.attributes["stats"]["crit"],
            "hit": self.attributes["stats"]["hit"],
            "tags": {}
        }

        if self.attributes["equipment"].get("weapon"):
            passives = []
            for effect in self.attributes["equipment"]["weapon"].attributes["effect"]:
                if effect.type == "passive":
                    passives += effect.attributes["value"]
                if effect.attributes["passive"]:
                    passives += effect.attributes["passive"]
            attackSkill.update({"passive": passives})

        if self.attributes["equipment"]:
            for slot in self.attributes["equipment"]:
                if slot == "weapon" or not self.attributes["equipment"][slot]:
                    continue
                if self.attributes["equipment"][slot].attributes["tags"]:
                    for tag, value in self.attributes["equipment"][slot].attributes["tags"].items():
                        if tag in ("variance", "pierce", "passive"):
                            attackSkill[tag] = copy.deepcopy(value)

        return [Effect(attackSkill)]

    def level_up(self):
        """
        Levels the Entity up if the Entity has enough xp.
        """

        while self.attributes["xp"] >= self.attributes["mxp"]:
            self.attributes["xp"] -= self.attributes["mxp"]
            self.attributes["mxp"] = math.ceil(self.attributes["mxp"] * 1.2)
            self.attributes["level"] += 1
            self.attributes["levelsGained"] += 1

            self.attributes["baseStats"]["max hp"] += self.attributes["extraStats"]["hpPerLevel"]
            self.attributes["baseStats"]["max mp"] += self.attributes["extraStats"]["mpPerLevel"]
            if self.attributes["level"] % 3 == 0:
                self.attributes["baseStats"]["strength"] += self.attributes["extraStats"]["strengthPerLevel"]
                self.attributes["baseStats"]["vitality"] += self.attributes["extraStats"]["vitalityPerLevel"]
                self.attributes["baseStats"]["intelligence"] += self.attributes["extraStats"]["intelligencePerLevel"]
            self.update_stats()

            self.attributes["hp"] = self.attributes["stats"]["max hp"]
            self.attributes["mp"] = self.attributes["stats"]["max mp"]

    def num_of_items(self, name):
        """
        Returns the number of Items in the inventory.

        Args:
            name:
                String name of the Item.

        Returns:
            Integer quantity.
        """

        num = 0
        for item in self.attributes["inventory"]:
            if item[0].attributes["name"] == name:
                num += item[1]

        return num

    def add_item(self, item, quantity=1):
        """
        Adds an item or items to the inventory.

        Args:
            item:
                Item to be added.
            quantity:
                Integer number of Items. Default is 1.
        """

        if not item:
            return

        # self.updateQuests(item=[item, quantity])
        if item.attributes["type"] in Globals.stackableItems:
            for i in self.attributes["inventory"]:
                if i[0].attributes["name"] == item.attributes["name"]:
                    i[1] += quantity
                    return
            self.attributes["inventory"].append([item, quantity])
        else:
            for i in range(quantity):
                self.attributes["inventory"].append([item, 1])

    def remove_item(self, item, quantity=1):
        """
        Removes an item or items from the inventory.

        Args:
            item:
                Item to be removed.
            quantity:
                Integer number of Items. Default is 1.
        """

        if not item:
            return

        if item.attributes["type"] in Globals.stackableItems:
            for i in self.attributes["inventory"]:
                if i[0].attributes["name"] == item.attributes["name"]:
                    i[1] -= quantity
                    if i[1] <= 0:
                        self.attributes["inventory"].remove([i[0], i[1]])
                    return
        else:
            for i in range(quantity):
                if [item, 1] in self.attributes["inventory"]:
                    self.attributes["inventory"].remove([item, 1])

    def unequip(self, slot):
        """
        Unequips an item from the equipment.

        Args:
            slot:
                String slot. See Globals.slotList.
        """

        self.add_item(self.attributes["equipment"][slot])
        self.attributes["equipment"][slot] = ""
        self.update_stats()

    def equip(self, item):
        """
        Equips an item to the equipment.

        Args:
            item:
                Item to be equipped.
        """

        if not item:
            return

        if item.attributes["slot"] == "accessory":
            if not self.attributes["equipment"].get("acc 1"):
                slot = "acc 1"
            else:
                slot = "acc 2"
        else:
            slot = item.attributes["slot"]

        if self.attributes["equipment"].get(slot):
            self.unequip(slot)
        self.attributes["equipment"][slot] = item
        self.remove_item(item)
        self.update_stats()

    def show_passives(self):
        if len(self.attributes["passives"]) > 0:
            text.slide_cursor(0, 3)
            print(", ".join([f'{passive.get_name(turns=True)}' for passive in self.attributes["passives"]]))

    def show_stats(self, gpxp=True, passives=True, small=False):
        """
        Show the stats of the entity.

        Args:
            gpxp:
                Boolean; if True, show gold and xp count. Default is True.
            passives:
                Boolean; if True, show Entity passives. Default is True.
            small:
                Boolean; if True, decrease the size of the bars. Default is false.
        """

        if small:
            barLength = 16
        else:
            barLength = 40

        print("")
        text.slide_cursor(1, 3)
        print(text.title(
            self.attributes["name"],
            self.attributes["level"],
            self.attributes.get("class", "")
        ))

        text.slide_cursor(0, 3)
        print(
            text.hp,
            text.bar(
                self.attributes["hp"],
                self.attributes["stats"]["max hp"],
                "red",
                length=barLength,
                number=True
            )
        )
        text.slide_cursor(0, 3)
        print(
            text.mp,
            text.bar(
                self.attributes["mp"],
                self.attributes["stats"]["max mp"],
                "blue",
                length=barLength,
                number=True
            )
        )

        if gpxp:
            text.slide_cursor(0, 3)
            print(
                text.xp,
                text.bar(
                    self.attributes["xp"],
                    self.attributes["mxp"],
                    "green",
                    length=barLength,
                    number=True
                )
            )

            text.slide_cursor(0, 3)
            print(text.gp, text.reset + str(self.attributes["gold"]))

        if passives:
            self.show_passives()

    def export(self):
        attributes = self.attributes.copy()
        for i in range(len(attributes["inventory"])):
            attributes["inventory"][i][0] = attributes["inventory"][i][0].export()
        for i in range(len(attributes["passives"])):
            attributes["passives"][i] = attributes["passives"][i].export()
        for slot in attributes["equipment"]:
            if attributes["equipment"][slot]:
                attributes["equipment"][slot] = attributes["equipment"][slot].export()
        return attributes

    """
    The Player Entity class.

    def __init__(self, attributes):
        Initializes the classes and sets up quests.

        Args:
            attributes:
                location:
                    String Player map name.
                quests:
                    List of active quests.
                mainQuests:
                    List of all main quests.
                mainQuest:
                    Integer index of current active main quest.
                completedQuests:
                    List of all completed quests.

        self.attributes = {
            "location": "magyka",
            "x": 128,
            "y": 113,
            "quests": [],
            "mainQuests": [],
            "mainQuest": 0,
            "completedQuests": [],
        }
        self.attributes.update(attributes)
        super().__init__(self.attributes)

        # for quest in self.attributes["mainQuests"]:
        #     quest.update({"main": True})
        # self.add_quest(self.attributes["mainQuests"][0])

        self.update_stats()

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
    """
