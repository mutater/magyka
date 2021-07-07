import copy
import script.Globals as Globals
from script.Text import text
from script.Control import control
from script.BaseClass import BaseClass


class Item(BaseClass):
    def __init__(self, attributes):
        self.defaults = {
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
                if type(enchantment.tags[tag]) is list:
                    tags.update({tag: enchantment.tags[tag][enchantment.tier]})
                else:
                    tags.update({tag: enchantment.tags[tag]})
            values.append(enchantment.value)
            for effect in enchantment.effect:
                if effect.type in Globals.statList:
                    effects.append(effect)
        
        # Sorting through tags to remove duplicate and deal with passive tags
        for tag in tags:
            tagFound = False
            if tag in self.tags:
                if type(self.tags[tag]) is int:
                    self.tags[tag] += tags[tag]
                else:
                    self.tags[tag] = tags[tag]
            else:
                if tag == "passive":
                    if self.effect[0].passive:
                        self.effect[0].passive.append(tags[tag])
                    else:
                        self.effect[0].passive = [tags[tag]]
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
    
    def get_name(self, info=False, quantity=0):
        hp = ""
        mp = ""
        symbol = ""
        symbolText = ""
        quantityText = ""
        typeText = ""
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
            
            typeText = self.type.capitalize()
        return f'{text.c(text.rarityColors[self.rarity])}{self.name.ljust(27 if info else 0)}{text.reset}{symbolText.ljust(8 if info else 0)}{quantityText}{typeText}'
    
    def show_stats(self):
        text.slide_cursor(1, 3)
        print(self.get_name())
        if self.type == "equipment":
            text.slide_cursor(0, 3)
            print(self.modifier.get_name())
        text.slide_cursor(0, 3)
        print(self.rarity.capitalize())
        
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
            effect.show_stats(stats=False)
        for passive in passives:
            passive.show_stats()
        for effect in effects:
            effect.show_stats(damage=False)
        if len(self.tags) > 0:
            print("")
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
        if "pierece" in self.tags:
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
        
        if self.enchantments:
            text.slide_cursor(1, 3)
            print(text.lightblue + "Enchantments:" + text.reset)
            for enchantment in self.enchantments:
                text.slide_cursor(0, 5)
                print(f'- {enchantment.return_name()}')
    
    def use(self, user, target):
        for effect in self.effect:
            text.slide_cursor(1, 3)
            print(f'{user.name} {self.text} {self.get_name()} on {target.name}, ', end="")
            target.defend(effect)


class Enchantment(BaseClass):
    def __init__(self, attributes):
        self.defaults = {
            "name": "Name",
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
                self.tags[tag] = self.baseTags[tag][tier] + self.increase[tier] * level
            for effect in self.effect:
                effect.value = effect.values[tier] + self.increase[tier] * level
    
    def return_name(self):
        return f'{self.name} {text.numeral(self.level)}'


class Modifier(BaseClass):
    def __init__(self, attributes):
        self.defaults = {
            "name": "Name",
            "rarity": "garbage",
            "value": "+0",
            "effect": [],
            "slot": "all",
            "tags": {}
        }
        
        super().__init__(attributes, self.defaults)
    
    def get_name(self):
        return text.c(text.rarityColors[self.rarity]) + self.name + text.reset
