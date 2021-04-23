from .Globals import *

class Item():
    def __init__(self, kwargs):
        for key, value in kwargs:
            setattr(self, key, value)
    
    def getValues(self):
        vars = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]

class Useable(Item):
    def __init__(self, kwargs):
        super().__init__(kwargs)
        self.effect = kwargs["effect"] if type(kwargs["effect"]) is list else [kwargs["effect"]]
        self.tags = kwargs["tags"]

class Equipment(Useable):
    def __init__(self, kwargs):
        super().__init__(kwargs)
        self.slot = kwargs["slot"]
        self.enchantment = kwargs["enchantment"]
        self.modifier = kwargs["modifier"]
        self.mana = kwargs["mana"]
        self.attackName = kwargs["attackName"]
        self.type = "equipment"

class Consumable(Useable):
    def __init__(self, kwargs):
        super().__init__(kwargs)
        self.useVerb = kwargs["useVerb"]
        self.target = kwargs["target"]
        self.type = "consumable"

