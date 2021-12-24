import copy
import random
import script.Globals as Globals
from script.Logger import logger
from script.Text import text


class Tags:
    """
    Class for displaying tags.
    """

    @staticmethod
    def show_tags(tags):
        """
        Prints the tags provided.

        Args:
            tags:
                Dict of tags.
        """

        if "hit" in tags:
            text.slide_cursor(0, 3)
            print("Accurate: Never misses")
            text.slide_cursor(0, 3)
            print("Seeking: Undodgeable")
        if "noMiss" in tags:
            text.slide_cursor(0, 3)
            print("Accurate: Never misses")
        if "noDodge" in tags:
            text.slide_cursor(0, 3)
            print("Seeking: Undodgeable")
        if "pierce" in tags:
            text.slide_cursor(0, 3)
            print(f'Piercing: Ignores {tags["pierce"]}% of enemy armor')
        if "variance" in tags:
            text.slide_cursor(0, 3)
            if tags["variance"] == 0:
                print("Unvarying: Damage does not vary")
            else:
                print(f'Varying: Damage varies by {tags["variance"]}%')
        if "infinite" in tags:
            text.slide_cursor(0, 3)
            print("Infinite: Item is not consumed upon use")
        if "lifesteal" in tags:
            text.slide_cursor(0, 3)
            print(f'Lifesteal: Heals for {tags["lifesteal"]}% of damage dealt')


class Item:
    """
    An Item. Dunno what to put here.
    """
    def __init__(self, attributes):
        """
        Initializes the class and fixes some variables if broken.

        Args:
            attributes:
                table:
                    String constant, "items".
                name:
                    String display name.
                description:
                    String display description.
                value:
                    Integer price in gold.
                rarity:
                    String rarity. See Globals.rarityList.
                type:
                    String type of item. "item", "consumable", "equipment".
                effect:
                    Effect.
                slot:
                    String slot the item equips to. See Globals.slotList.
                target:
                    String target of the Item Effect. "self" or "enemy". Defaults to "enemy".
                text:
                    String text displayed when used.
                enchantments:
                    List of Enchantments.
                modifier:
                    Modifier.
                tags:
                    Dict of any extra information.
        """

        self.attributes = {
            "table": "items",
            "name": "Name",
            "description": "Description",
            "value": 0,
            "rarity": "garbage",
            "type": "item",
            "effect": [],
            "slot": None,
            "target": "enemy",
            "text": "uses",
            "enchantments": [],
            "modifier": None,
            "tags": {}
        }
        self.attributes.update(attributes)
        
        if "effect" in self.attributes:
            self.attributes["baseEffect"] = copy.deepcopy(self.attributes["effect"])
        if "tags" in self.attributes:
            self.attributes["baseTags"] = copy.deepcopy(self.attributes["tags"])
        if "value" in self.attributes:
            self.attributes["baseValue"] = copy.deepcopy(self.attributes["value"])
        
        if type(self.attributes["effect"]) != list:
            self.attributes["effect"] = [self.attributes["effect"]]
        
        if self.attributes["type"] == "equipment":
            self.update()
    
    def update(self):
        """
        Updates the Item by refreshing effects, tags, and value.
        """

        self.attributes["effect"] = copy.deepcopy(self.attributes["baseEffect"])
        self.attributes["tags"] = copy.deepcopy(self.attributes["baseTags"])
        self.attributes["value"] = self.attributes["baseValue"]
        
        # Getting the names of all enchantment and modifier stats
        statNames = []
        if self.attributes["modifier"].attributes["effect"]:
            statNames = [effect.attributes["type"] for effect in self.attributes["modifier"].attributes["effect"]]
        if self.attributes["enchantments"]:
            for enchantment in self.attributes["enchantments"]:
                for effect in enchantment.attributes["effect"]:
                    statNames.append(effect.attributes["type"])
        effects = []
        tags = {}
        values = [self.attributes["modifier"].attributes["value"]]
        
        # Adding all enchantment and modifier effects, tags, and values to their respective lists
        tags.update(self.attributes["modifier"].attributes["tags"])
        for effect in self.attributes["modifier"].attributes["effect"]:
            if effect.attributes["type"] in Globals.statList:
                effects.append(effect)
        
        for enchantment in self.attributes["enchantments"]:
            for tag in enchantment.attributes["tags"]:
                if tag == "passive":
                    tags.update({"passive": enchantment.attributes["tags"][tag]})
                else:
                    if type(enchantment.attributes["tags"][tag]) is list:
                        tags.update({tag: enchantment.attributes["tags"][tag][enchantment.tier]})
                    else:
                        tags.update({tag: enchantment.attributes["tags"][tag]})

            values.append(enchantment.attributes["value"])

            for effect in enchantment.attributes["effect"]:
                if effect.attributes["type"] in Globals.statList:
                    effects.append(effect)
        
        # Sorting through tags to remove duplicate and deal with passive tags
        for tag in tags:
            if tag in self.attributes["tags"]:
                if type(self.attributes["tags"][tag]) is int:
                    self.attributes["tags"][tag] += tags[tag]
                else:
                    self.attributes["tags"][tag] = tags[tag]
            else:
                if tag == "passive":
                    if self.attributes["effect"][0].attributes["passive"]:
                        self.attributes["effect"][0].attributes["passive"] += copy.deepcopy(tags[tag])
                    else:
                        self.attributes["effect"][0].passive = copy.deepcopy(tags[tag])
                else:
                    self.attributes["tags"].update({tag: tags[tag]})
        
        # Calculating the value of the item from the values in values
        for value in values:
            if value[0] == "+":
                self.attributes["value"] += int(value[1:])
            elif value[0] == "-":
                self.attributes["value"] -= int(value[1:])
            elif value[0] == "*":
                self.attributes["value"] = round(float(value[1:]) * self.attributes["value"])
        
        # Adding the stats in statNames that the item currently doesn't have
        for statName in statNames:
            statFound = False
            for effect in self.attributes["effect"]:
                if statName == effect.attributes["type"]:
                    statNames = [statName for statName in statNames if statName != effect.attributes["type"]]
                    statFound = True
                    break

            if not statFound:
                self.attributes["effect"].append({"type": statName, "value": 0})

        # Adding every effect provided by enchantments and modifiers to the item
        for effect in effects:
            for selfEffect in self.attributes["effect"]:
                if effect.attributes["type"] == selfEffect.attributes["type"]:
                    if selfEffect.attributes["opp"] == "*":
                        selfEffect.attributes["value"] = round(
                            selfEffect.attributes["value"]
                            * ((effect.attributes["value"] / 100) + 1))
                    else:
                        selfEffect.attributes["value"] += effect.attributes["value"]
    
    def modify(self, modifier):
        """
        Adds a modifier to the item.

        Args:
            modifier:
                Modifier to be added.
        """

        if not modifier:
            return

        self.attributes["modifier"] = modifier
        
        self.update()
    
    def enchant(self, enchantment):
        """
        Formats then adds an Enchantment to the Item.

        Args:
            enchantment:
                Enchantment to be added.
        """

        if not enchantment:
            return
        
        # Looping through item enchantments to combine the enchantment or check for duplicates
        enchantmentFound = False
        for i in range(len(self.attributes["enchantments"])):
            selfEnchantment = self.attributes["enchantment"][i]

            if selfEnchantment.attributes["name"] == enchantment.attributes["name"]:
                enchantmentFound = True
                if selfEnchantment.attributes["level"] == enchantment.attributes["level"]\
                        and selfEnchantment.attributes["level"] < selfEnchantment.attributes["maxLevel"]:
                    self.attributes["enchantment"][i] = selfEnchantment.update(
                        selfEnchantment.attributes["tier"],
                        selfEnchantment.attributes["level"] + 1
                    )
                elif selfEnchantment.attributes["level"] < enchantment.attributes["level"]:
                    self.attributes["enchantment"][i] = enchantment
                break

        if not enchantmentFound:
            self.attributes["enchantments"].append(enchantment)
        
        self.update()
    
    def get_name(self, info=False, value=False, quantity=0):
        """
        Returns the name of the Item.

        Args:
            info:
                Boolean; if True, show info such as value and effect. Default is False.
            value:
                Boolean; if True, show value. Default is False.
            quantity:
                Integer; if > 0, show quantity of item. Default is 0.

        Returns:
            String containing ANSI color.
        """

        hp = ""
        mp = ""
        symbol = ""
        symbolText = ""
        quantityText = ""
        typeText = ""
        valueText = ""

        if info:
            for effect in self.attributes["effect"]:
                if effect.attributes["type"] == "healHp" and not self.attributes["slot"]:
                    hp = "♥"
                if effect.attributes["type"] == "healMp" and not self.attributes["slot"]:
                    mp = "♦"
            
            if hp or mp or symbol:
                symbolText = f' {symbol}{hp}{mp}'
            
            if quantity and self.attributes["type"] != "equipment":
                quantityText = " x" + str(quantity).ljust(5)
            else:
                quantityText = "       "
            
            typeText = self.attributes["type"].capitalize().ljust(11)
            
            if value:
                valueText = text.gp + text.reset + " " + str(self.attributes["value"])

        return (
            f'{text.c(text.rarityColors[self.attributes["rarity"]])}'
            f'{self.attributes["name"].ljust(27 if info else 0)}'
            f'{text.reset}'
            f'{symbolText.ljust(8 if info else 0)}'
            f'{quantityText}{typeText}{valueText}'
        )
    
    def show_stats(self):
        """
        Shows the stats of the item, omitting tag, modifier, and enchantment details.
        """
        text.slide_cursor(1, 3)
        print(self.get_name())
        if self.attributes["type"] == "equipment":
            text.slide_cursor(0, 3)
            print(self.attributes["modifier"].get_name())
        text.slide_cursor(0, 3)
        
        effects = []
        passives = []
        if self.attributes["type"] not in ("modifier", "item"):
            for effect in self.attributes["effect"]:
                if effect.attributes["type"] == "passive":
                    for passive in effect.attributes["passive"]:
                        passives.append(passive)
                elif effect.attributes["type"] == "stat":
                    effects.append(effect)
                else:
                    if effect.attributes["passive"]:
                        for passive in effect.attributes["passive"]:
                            passives.append(passive)
                    effects.append(effect)

        print("")
        for effect in effects:
            effect.show_damage()
        for passive in passives:
            passive.show_stats()
        for effect in effects:
            effect.show_stats()
        if len(self.attributes["tags"]) > 0:
            text.slide_cursor(0, 3)
            i = 0
            for tag in self.attributes["tags"]:
                print(tag.capitalize(), end="")
                if i < len(self.attributes["tags"]) - 1 and len(self.attributes["tags"]) > 2:
                    print(", ", end="")
                if i == len(self.attributes["tags"]) - 2:
                    if len(self.attributes["tags"]) < 3:
                        print(" ", end="")
                    print("and ", end="")
                i += 1
            print("")
        
        if self.attributes["enchantments"]:
            text.slide_cursor(1, 3)
            print(f'{text.purple}Enchanted{text.reset}')
        
    def show_stats_detailed(self):
        """
        Shows the stats of the item in regards to enchantments, modifier, and tags.
        """

        text.slide_cursor(1, 3)
        print(self.attributes["modifier"].get_name())

        if self.attributes["enchantments"]:
            text.slide_cursor(1, 3)
            print(f'{text.purple}Enchantments:{text.reset}')
            for enchantment in self.attributes["enchantments"]:
                text.slide_cursor(0, 5)
                print(f'- {enchantment.return_name()}')
                text.slide_cursor(0, 5)
                enchantment.show_stats()
        print("")

        Tags.show_tags(self.attributes["tags"])
    
    def use(self, user, target, item=False):
        """
        Uses the item on an Entity or Item.

        Args:
            user:
                Entity using the Item.
            target:
                Entity target.
            item:
                Boolean; if True, target is an item. Default is False.
        """

        if not item:
            print("")
            text.slide_cursor(0, 3)
            if self.attributes["target"] == "self":
                print(
                    f'{user.attributes["name"]} '
                    f'{self.attributes["text"]} '
                    f'{self.get_name()}, ',
                    end=""
                )
            else:
                print(
                    f'{user.attributes["name"]} '
                    f'{self.attributes["text"]} '
                    f'{self.get_name()} on {target.attributes["name"]}, ',
                    end=""
                )
                
                if random.randint(1, 100) > user.attributes["stats"]["hit"] and\
                        not (self.attributes["tags"].get("noMiss") or self.attributes["tags"].get("hit")):
                    print("but misses.")
                    return
                elif random.randint(1, 100) <= target.attributes["stats"]["dodge"] and\
                        not (self.attributes["tags"].get("noDodge") or self.attributes["tags"].get("hit")):
                    print(f'but {target.attributes["name"]} dodges.')
                    return
            
            for i in range(len(self.attributes["effect"])):
                target.defend(self.attributes["effect"][i], tags=self.attributes["tags"])
                if len(self.attributes["effect"]) > 2:
                    print(", ", end="")
                if i < len(self.attributes["effect"]) - 1:
                    print(" and")
                    text.slide_cursor(0, 4)
            print(".")

            if self.attributes["tags"].get("loot"):
                items = self.attributes["tags"]["loot"].use()
                if not self.attributes["effect"]:
                    text.slide_cursor(1, 3)
                    print(
                        f'{user.attributes["name"]} '
                        f'{self.attributes["text"]} '
                        f'{self.get_name()}, receiving:',
                        end=""
                    )

                for i in range(len(items)):
                    quantity = items[i][1] if items[i][0].attributes["type"] != "equipment" else 0
                    print(f'{items[i][0].get_name(quantity=quantity)}')
                    if i == len(items) - 2:
                        print("and ", end="")
                    target.add_item(items[i][0], items[i][1])
        else:
            if self.attributes["enchantments"]:
                for enchantment in self.attributes["enchantments"]:
                    target.enchant(enchantment)
            target.update()

    def export(self):
        attributes = copy.deepcopy(self.attributes)

        for i in range(len(attributes["effect"])):
            attributes["effect"][i] = attributes["effect"][i].export()
        for i in range(len(attributes["baseEffect"])):
            attributes["baseEffect"][i] = attributes["baseEffect"][i].export()
        for i in range(len(attributes["enchantments"])):
            attributes["enchantments"][i] = attributes["enchantments"][i].export()

        if attributes["tags"].get("passive"):
            for i in range(len(attributes["tags"]["passive"])):
                attributes["tags"]["passive"][i] = attributes["tags"]["passive"][i].export()
        if attributes["baseTags"].get("passive"):
            for i in range(len(attributes["baseTags"]["passive"])):
                attributes["baseTags"]["passive"][i] = attributes["baseTags"]["passive"][i].export()

        if attributes["tags"].get("loot"):
            attributes["tags"]["loot"] = attributes["tags"]["loot"].export()
        if attributes["baseTags"].get("loot"):
            attributes["baseTags"]["loot"] = attributes["baseTags"]["loot"].export()
        if attributes["modifier"]:
            attributes["modifier"] = attributes["modifier"].export()

        return attributes


class Enchantment:
    """
    Class containing an Enchantment for an Item.
    """
    def __init__(self, attributes):
        """
        Initializes the class.

        Args:
            attributes:
                table:
                    String constant, "enchantments".
                name:
                    String display name.
                type:
                    String constant, "Enchantment".
                baseName:
                    String Enchantment name.
                maxLevel:
                    Integer highest level of the enchantment.
                effect:
                    List of Effects.
                increase:
                    List of how much Effect value increases per level and tier.

                    e.g. [1, 2, 4] for [tier 0, tier 1, tier 2].
                valueIncrease:
                    List of how much value increases per level and tier.

                    e.g. [1, 2, 4] for [tier 0, tier 1, tier 2].
                slot:
                    Slot the Enchantment applies to. See Globals.slotList.

                    Slot can also be "armor".
                level:
                    Integer level of the Enchantment.
                tags:
                    Dict of any extra information.
        """

        self.attributes = {
            "table": "enchantments",
            "name": "Name",
            "type": "Enchantment",
            "baseName": "Name",
            "maxLevel": 10,
            "effect": [],
            "increase": [],
            "valueIncrease": [],
            "slot": None,
            "level": 1,
            "tags": {}
        }
        self.attributes.update(attributes)
        
        self.attributes["baseTags"] = copy.deepcopy(self.attributes["tags"])
        
    def update(self, tier, level):
        """
        Updates the enchantment to a new tier and level.

        Args:
            tier:
                Integer.
            level:
                Level.
        """

        if tier == 0:
            self.attributes["name"] = "Lesser " + self.attributes["baseName"]
        elif tier == 2:
            self.attributes["name"] = "Advanced " + self.attributes["baseName"]
        
        self.attributes["value"] = "+" + str(self.attributes["valueIncrease"][tier] * level)
        
        for tag in self.attributes["tags"]:
            self.attributes["tags"][tag] = self.attributes["tags"][tag][tier]

        if self.attributes["increase"]:
            for tag in self.attributes["tags"]:
                if self.attributes["tags"][tag] != "passive":
                    self.attributes["tags"][tag] = (
                        self.attributes["baseTags"][tag][tier]
                        + self.attributes["increase"][tier] * level - 1
                    )
            for effect in self.attributes["effect"]:
                effect.attributes["value"] = (
                    effect.attributes["values"][tier]
                    + self.attributes["increase"][tier] * level - 1
                )
    
    def return_name(self):
        return f'{self.attributes["name"]} {text.numeral(self.attributes["level"])}'
    
    def show_stats(self):
        for effect in self.attributes["effect"]:
            effect.show_stats()
        Tags.show_tags(self.attributes["tags"])

    def export(self):
        attributes = copy.deepcopy(self.attributes)

        for i in range(len(attributes["effect"])):
            attributes["effect"][i] = attributes["effect"][i].export()

        if attributes["tags"].get("passive"):
            for i in range(len(attributes["tags"]["passive"])):
                attributes["tags"]["passive"][i] = attributes["tags"]["passive"][i].export()
        if attributes["baseTags"].get("passive"):
            for i in range(len(attributes["baseTags"]["passive"])):
                if type(attributes["baseTags"]["passive"][i]) is list:
                    for j in range(len(attributes["baseTags"]["passive"][i])):
                        attributes["baseTags"]["passive"][i][j] = attributes["baseTags"]["passive"][i][j].export()
                else:
                    attributes["baseTags"]["passive"][i] = attributes["baseTags"]["passive"][i].export()

        return attributes


class Modifier:
    """
    Class containing a Modifier for an Item.
    """
    def __init__(self, attributes):
        """
        Initializes the class.

        Args:
            attributes:
                table:
                    String constant, "modifiers".
                name:
                    String display name.
                type:
                    String constant, "Modifier".
                rarity:
                    String rarity. See Globals.rarityList.
                value:
                    String amount that Modifier influences Item value.

                    First character is "+" or "*".
                    The rest of the string is an integer.
                effect:
                    Effect.
                slot:
                    String slot the Modifier effects. See Globals.slotList.

                    Slot can also be "armor".
                tags:
                    Dict of any extra information.
        """

        self.attributes = {
            "table": "modifiers",
            "name": "Name",
            "type": "Modifier",
            "rarity": "garbage",
            "value": "+0",
            "effect": [],
            "slot": "all",
            "tags": {}
        }
        self.attributes.update(attributes)
    
    def get_name(self):
        return text.c(text.rarityColors[self.attributes["rarity"]]) + self.attributes["name"] + text.reset
    
    def show_stats(self):
        if self.attributes["name"] == "normal":
            print("No effect")
            return
        for effect in self.attributes["effect"]:
            effect.show_stats()
        Tags.show_tags(self.attributes["tags"])

    def export(self):
        attributes = copy.deepcopy(self.attributes)

        for i in range(len(attributes["effect"])):
            attributes["effect"][i] = attributes["effect"][i].export()

        if attributes["tags"].get("passive"):
            for i in range(len(attributes["tags"]["passive"])):
                attributes["tags"]["passive"][i] = attributes["tags"]["passive"][i].export()

        return attributes
