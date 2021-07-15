import copy
import json
import script.Globals as Globals
from script.BaseClass import BaseClass
from script.Control import control
from script.Entity import Entity, Player, Enemy
from script.Logger import logger
from script.Text import text


class Tags:
    def show_tags(self):
        if "hit" in self.tags:
            text.slide_cursor(0, 3)
            print("Accurate: Never misses")
            text.slide_cursor(0, 3)
            print("Seeking: Undodgeable")
        if "noMiss" in self.tags:
            text.slide_cursor(0, 3)
            print("Accurate: Never misses")
        if "noDodge" in self.tags:
            text.slide_cursor(0, 3)
            print("Seeking: Undodgeable")
        if "pierce" in self.tags:
            text.slide_cursor(0, 3)
            print(f'Piercing: Ignores {self.tags["pierce"]}% of enemy armor')
        if "variance" in self.tags:
            text.slide_cursor(0, 3)
            if self.tags["variance"] == 0:
                print("Unvarying: Damage does not vary")
            else:
                print(f'Varying: Damage varies by {self.tags["variance"]}%')
        if "infinite" in self.tags:
            text.slide_cursor(0, 3)
            print("Infinite: Item is not consumed upon use")
        if "lifesteal" in self.tags:
            text.slide_cursor(0, 3)
            print(f'Lifesteal: Heales for {self.tags["lifesteal"]}% of damage dealt')


class Item(BaseClass, Tags):
    def __init__(self, attributes):
        self.defaults = {
            "table": "items",
            "name": "Name",
            "description": "Description",
            "value": 0,
            "rarity": "garbage",
            "type": "item",
            "effect": [],
            "slot": None,
            "mana": 0,
            "target": "enemy",
            "text": "uses",
            "enchantments": [],
            "tags": {},
            "modifier": None
        }
        
        super().__init__(attributes, self.defaults)
        
        if "effect" in attributes:
            self.baseEffect = copy.deepcopy(attributes["effect"])
        if "tags" in attributes:
            self.baseTags = copy.deepcopy(attributes["tags"])
        if "value" in attributes:
            self.baseValue = copy.deepcopy(attributes["value"])
        
        if type(self.effect) != list:
            self.effect = [self.effect]
        
        if self.type == "equipment":
            self.update()

    def getValues(self):
        return [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]
    
    def update(self):
        self.effect, self.tags, self.value = copy.deepcopy(self.baseEffect), copy.deepcopy(self.baseTags), self.baseValue
        
        # Getting the names of all enchantment and modifier stats
        statNames = []
        if self.modifier.effect:
            statNames = [effect.type for effect in self.modifier.effect]
        if self.enchantments:
            for enchantment in self.enchantments:
                for effect in enchantment.effect:
                    statNames.append(effect.type)
        effects, tags, values = [], {}, []
        
        # Adding all enchantment and modifier effects, tags, and values to their respective lists
        values.append(self.modifier.value)
        
        tags.update(self.modifier.tags)
        for effect in self.modifier.effect:
            if effect.type in Globals.statList:
                effects.append(effect)
        
        for enchantment in self.enchantments:
            for tag in enchantment.tags:
                if tag == "passive":
                    tags.update({"passive": enchantment.tags[tag]})
                else:
                    if type(enchantment.tags[tag]) is list:
                        tags.update({tag: enchantment.tags[tag][enchantment.tier]})
                    else:
                        tags.update({tag: enchantment.tags[tag]})
            values.append(enchantment.value)
            for effect in enchantment.effect:
                if effect.type in Globals.statList:
                    effects.append(effect)
        
        # Sorting through tags to remove duplicate and deal with passive tags
        logger.log(tags)
        for tag in tags:
            if tag in self.tags:
                if type(self.tags[tag]) is int:
                    self.tags[tag] += tags[tag]
                else:
                    self.tags[tag] = tags[tag]
            else:
                if tag == "passive":
                    for passive in tags[tag]:
                        if self.effect[0].passive:
                            self.effect[0].passive += copy.deepcopy(tags[tag])
                        else:
                            self.effect[0].passive = copy.deepcopy(tags[tag])
                else:
                    self.tags.update({tag: tags[tag]})
        
        # Calculating the value of the item from the values in values
        for value in values:
            if value[0] == "+":
                self.value += int(value[1:])
            elif value[0] == "-":
                self.value -= int(value[1:])
            elif value[0] == "*":
                self.value = round(float(value[1:]) * self.value)
        
        # Adding the stats in statNames that the item currently doesn't have
        for statName in statNames:
            statFound = False
            for effect in self.effect:
                if statName == effect.type:
                    statNames = [statName for statName in statNames if statName != effect.type]
                    statFound = True
                    break
            if not statFound:
                self.effect.append({"type": statName, "value": 0})

        # Adding every effect provided by enchantments and modifiers to the item
        for effect in effects:
            for selfEffect in self.effect:
                if effect.type == selfEffect.type:
                    if selfEffect.type == "attack":
                        for i in range(2):
                            if effect.opp == "*":
                                selfEffect.value[i] = round(selfEffect.value[i] * ((effect.value / 100) + 1))
                            else:
                                selfEffect.value[i] += effect.value
                    else:
                        if selfEffect.opp == "*":
                            round(selfEffect.value * ((effect.value / 100) + 1))
                        else:
                            selfEffect.value += effect.value
    
    def modify(self, modifier):
        if not modifier:
            return

        self.modifier = modifier
        
        self.update()
    
    def enchant(self, enchantment):
        if not enchantment:
            return
        
        # Looping through item enchantments to combine the enchantment or check for duplicates
        enchantmentFound = False
        for i in range(len(self.enchantments)):
            if self.enchantments[i].name == self.name:
                enchantmentFound = True
                if self.enchantments[i].level == enchantment.level and self.enchantments[i].level < self.enchantments[i].maxLevel:
                    self.enchantments[i] = self.enchantments[i].update(self.enchantments[i].tier, self.enchantments[i].level + 1)
                elif self.enchantments[i].level < enchantment.level:
                    self.enchantments[i] = enchantment
                break
        if not enchantmentFound:
            self.enchantments.append(enchantment)
        
        self.update()
    
    def get_name(self, info=False, value=False, quantity=0):
        hp = ""
        mp = ""
        symbol = ""
        symbolText = ""
        quantityText = ""
        typeText = ""
        valueText = ""
        if info:
            for effect in self.effect:
                if effect.type == "healHp" and not self.slot:
                    hp = "♥"
                if effect.type == "healMp" and not self.slot:
                    mp = "♦"
            
            if hp or mp or symbol:
                symbolText = f' {symbol}{hp}{mp}'
            
            if quantity and self.type != "equipment":
                quantityText = " x" + str(quantity).ljust(5)
            else:
                quantityText = "       "
            
            typeText = self.type.capitalize().ljust(11)
            
            if value:
                valueText = text.gp + text.reset + " " + str(self.value)
        return f'{text.c(text.rarityColors[self.rarity])}{self.name.ljust(27 if info else 0)}{text.reset}{symbolText.ljust(8 if info else 0)}{quantityText}{typeText}{valueText}'
    
    def show_stats(self):
        text.slide_cursor(1, 3)
        print(self.get_name())
        if self.type == "equipment":
            text.slide_cursor(0, 3)
            print(self.modifier.get_name())
        text.slide_cursor(0, 3)
        
        effects = []
        passives = []
        if self.type not in ("modifier", "item"):
            for effect in self.effect:
                if effect.type == "passive":
                    for passive in effect.passive:
                        passives.append(passive)
                elif effect.type == "stat":
                    effects.append(effect)
                else:
                    if effect.passive:
                        for passive in effect.passive:
                            passives.append(passive)
                    effects.append(effect)
        
        if self.type == "equipment" and self.slot == "tome":
            text.slide_cursor(0, 3)
            print(f'Costs {text.blue}{self.mana} ♦{text.reset}')
        print("")
        for effect in effects:
            effect.show_stats(stats=False, passive=False)
        for passive in passives:
            passive.show_stats()
        for effect in effects:
            effect.show_stats(damage=False, passive=False)
        if len(self.tags) > 0:
            text.slide_cursor(0, 3)
            i = 0
            for tag in self.tags:
                print(tag.capitalize(), end="")
                if i < len(self.tags) - 1 and len(self.tags) > 2:
                    print(", ", end="")
                if i == len(self.tags) - 2:
                    if len(self.tags) < 3:
                        print(" ", end="")
                    print("and ", end="")
                i += 1
            print("")
        
        if self.enchantments:
            text.slide_cursor(1, 3)
            print(f'{text.lightblue}Enchanted{text.reset}')
        
    def show_stats_detailed(self):
        text.slide_cursor(1, 3)
        print(self.modifier.get_name())
        if self.enchantments:
            text.slide_cursor(1, 3)
            print(text.lightblue + "Enchantments:" + text.reset)
            for enchantment in self.enchantments:
                text.slide_cursor(0, 5)
                print(f'- {enchantment.return_name()}')
                text.slide_cursor(0, 5)
                enchantment.show_stats()
        print("")
        super().show_tags()
    
    def use(self, user, target, item=False):
        if not item:
            for effect in self.effect:
                text.slide_cursor(1, 3)
                if self.target == "self":
                    print(f'{user.name} {self.text} {self.get_name()}, ', end="")
                else:
                    print(f'{user.name} {self.text} {self.get_name()} on {target.name}, ', end="")
                target.defend(effect, tags=self.tags)
            if self.target == "self" and self.tags.get("loot"):
                items = self.tags["loot"].use()
                if not self.effect:
                    text.slide_cursor(1, 3)
                    print(f'{user.name} {self.text} {self.get_name()}, ', end="")
                print(f'receiving:')
                for i in range(len(items)):
                    quantity = items[i][0].type != "equipment"
                    print(f'{items[i][0].get_name(quantity=(items[i][1] if quantity else 0))}')
                    if i == len(items) - 2:
                        print("and ", end="")
                    target.add_item(items[i][0], items[i][1])
                    
    def export(self):
        for i in range(len(self.effect)):
            self.effect[i] = self.effect[i].export()
        for i in range(len(self.baseEffect)):
            self.baseEffect[i] = self.baseEffect[i].export()
        for i in range(len(self.enchantments)):
            self.enchantments[i] = self.enchantments[i].export()
        if self.tags.get("passive"):
            for i in range(len(self.tags["passive"])):
                self.tags["passive"][i] = self.tags["passive"][i].export()
        if self.baseTags.get("passive"):
            for i in range(len(self.baseTags["passive"])):
                self.baseTags["passive"][i] = self.baseTags["passive"][i].export()
        if self.tags.get("loot"):
            self.tags["loot"] = self.tags["loot"].export()
        if self.baseTags.get("loot"):
            self.baseTags["loot"] = self.baseTags["loot"].export()
        if self.modifier:
            self.modifier = self.modifier.export()
        return super().export()


class Enchantment(BaseClass, Tags):
    def __init__(self, attributes):
        self.defaults = {
            "table": "enchantments",
            "name": "Name",
            "type": "Enchantment",
            "baseName": "Name",
            "maxLevel": 10,
            "effect": [],
            "increase": [],
            "valueIncrease": [],
            "slot": None,
            "tags": {},
            "level": 1
        }
        
        super().__init__(attributes, self.defaults)
        
        self.baseTags = copy.deepcopy(self.tags)
        
    
    def update(self, tier, level):
        if tier == 0:
            self.name = "Lesser " + self.baseName
        elif tier == 2:
            self.name = "Advanced " + self.baseName
        
        self.value = "+" + str(self.valueIncrease[tier] * level)
        
        for tag in self.tags:
            self.tags[tag] = self.tags[tag][tier]
        if self.increase:
            for tag in self.tags:
                if self.tags[tag] != "passive":
                    self.tags[tag] = self.baseTags[tag][tier] + self.increase[tier] * level
            for effect in self.effect:
                effect.value = effect.values[tier] + self.increase[tier] * level
    
    def return_name(self):
        return f'{self.name} {text.numeral(self.level)}'
    
    def show_stats(self):
        for effect in self.effect:
            effect.show_stats(damage=False)
        super().show_tags()
    
    def export(self):
        for i in range(len(self.effect)):
            self.effect[i] = self.effect[i].export()
        if self.tags.get("passive"):
            for i in range(len(self.tags["passive"])):
                self.tags["passive"][i] = self.tags["passive"][i].export()
        if self.baseTags.get("passive"):
            for i in range(len(self.baseTags["passive"])):
                for j in range(len(self.baseTags["passive"][i])):
                    self.baseTags["passive"][i][j] = self.baseTags["passive"][i][j].export()
        return super().export()


class Modifier(BaseClass, Tags):
    def __init__(self, attributes):
        self.defaults = {
            "table": "modifiers",
            "name": "Name",
            "type": "Modifier",
            "rarity": "garbage",
            "value": "+0",
            "effect": [],
            "slot": "all",
            "tags": {}
        }
        
        super().__init__(attributes, self.defaults)
    
    def get_name(self):
        return text.c(text.rarityColors[self.rarity]) + self.name + text.reset
    
    def show_stats(self):
        if self.name == "normal":
            print("No effect")
            return
        for effect in self.effect:
            effect.show_stats()
        super().show_tags()

    def export(self):
        for i in range(len(self.effect)):
            self.effect[i] = self.effect[i].export()
        if self.tags.get("passive"):
            for i in range(len(self.tags["passive"])):
                self.tags["passive"][i] = self.tags["passive"][i].export()
        return super().export()
