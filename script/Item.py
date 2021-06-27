import copy

class Item():
    def __init__(self, kwargs):
        for key in kwargs:
            setattr(self, key, kwargs[key])
        
        if "effect" in kwargs:
            self.baseEffect = copy.deepcopy(kwargs["effect"])
        if "tags" in kwargs:
            self.baseTags = copy.deepcopy(kwargs["tags"])
        if "value" in kwargs:
            self.baseValue = copy.deepcopy(kwargs["value"])
        
        if type(self.effect) != list:
            self.effect = [self.effect]
        
        if self.type == "equipment": self.update()
    
    
    def getValues(self):
        return [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]
    
    
    def update(self):
        self.effect, self.tags, self.value = copy.deepcopy(self.baseEffect), copy.deepcopy(self.baseTags), self.baseValue
        
        # Getting the names of all enchantment and modifier stats
        statNames = []
        if self.modifier.effect != []: statNames = [effect["type"] for effect in self.modifier.effect]
        if item.enchantments != []: statNames += [effect["type"] for effect in [enchantment["effect"] for enchantment in item.enchantments][0]]
        effects, tags, values = [], [], []
        
        # Adding all enchantment and modifier effects, tags, and values to their respective lists
        values.append(self.modifier.value)
        
        tags += self.modifier.tags
        for effect in self.modifier.effect:
            if effect["type"] in Entity(0, 0, 0, 0, {}).stats: effects.append(effect)
        
        for enchantment in item.enchantments:
            tags += enchantment["effect"]
            values.append(enchantment["effect"])
            for effect in enchantment["effect"]:
                if effect["type"] in  Entity(0, 0, 0, 0, {}).stats: effects.append(effect)
        
        # Sorting through tags to remove duplicate and deal with passive tags
        for tag in tags:
            name = tag.split(":")[0]
            try: value = tag.split(":")[1]
            except: value = False
            tagFound = False
            for t in item.tags:
                if name == t.split(":")[0]:
                    if len(t.split(":")) == 1 or not value:
                        tagFound = True
                        break
                    else:
                        tagFound = True
                        item.tags.append(name + ":" + str(int(value) + int(t.split(":")[1])))
                        item.tags.remove(t)
            if not tagFound:
                if name == "passive":
                    if "passive" in item.effect[0]: item.effect[0].passive.append(value)
                    else: item.effect[0].update({"passive": [value]})
                else: item.tags.append(tag)
        
        # Calculating the value of the item from the values in values
        for value in values:
            if value[0] == "+": self.value += int(value[1:])
            elif value[0] == "-": self.value -= int(value[1:])
            elif value[0] == "*": self.value = round(float(value[1:]) * self.value)

        # Adding the stats in statNames that the item currently doesn't have
        for statName in statNames:
            statFound = False
            for effect in item.effect:
                if statName == effect["type"]:
                    statNames = [statName for statName in statNames if statName != effect["type"]]
                    statFound = True
                    break
            if not statFound: item.effect.append({"type": statName, "value": 0})

        # Adding every effect provided by enchantments and modifiers to the item
        for e in effects:
            for effect in item.effect:
                if e.type == effect["type"]:
                    if effect["type"] == "attack":
                        for i in range(2):
                            if "*" in e: effect["value"][i] = round(effect["value"][i] * ((e.value / 100) + 1))
                            else: effect["value"][i] += e.value
                    else:
                        if "*" in effect: round(effect["value"] * ((e.value / 100) + 1))
                        else: effect["value"] += e.value
        return item
    
    
    def modifyEquipment(self, modifier):
        if modifier == None: return

        self.modifier = modifier
        
        self.update()
    
    
    def enchant(self, enchantment):
        if enchantment == None: return
        
        # Looping through item enchantments to combine the enchantment or check for duplicates
        enchantmentFound = False
        for i in range(len(self.enchantments)):
            if self.enchantments[i]["name"] == enchantment["name"]:
                enchantmentFound = True
                if self.enchantments[i]["level"] == enchantment["level"] and self.enchantments[i]["level"] < self.enchantments[i]["maxLevel"]:
                    self.enchantments[i] = newEnchantment(self.enchantments[i]["real name"], self.enchantments[i]["tier"], self.enchantments[i]["level"] + 1)
                elif self.enchantments[i]["level"] < enchantment["level"]:
                    self.enchantments[i]["level"] = enchantment["level"]
                break
        if not enchantmentFound: self.enchantments.append(enchantment)
        
        self.update()
