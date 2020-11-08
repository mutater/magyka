from .Globals import *

class Item():
    def __init__(self, kwargs):
        self.name = kwargs["name"]
        self.description = kwargs["description"]
        self.rarity = kwargs["rarity"]
        self.value = kwargs["value"]
        self.type = "item"

class Equipment():
    def __init__(self, kwargs):
        self.name = kwargs["name"]
        self.description = kwargs["description"]
        self.rarity = kwargs["rarity"]
        self.value = kwargs["value"]
        self.slot = kwargs["slot"]
        self.effect = kwargs["effect"] if type(kwargs["effect"]) is list else [kwargs["effect"]]
        self.enchantment = kwargs["enchantment"]
        self.modifier = kwargs["modifier"]
        self.mana = kwargs["mana"]
        self.attackName = kwargs["attackName"]
        self.attackSound = kwargs["attackSound"]
        self.type = "equipment"

class Consumable():
    def __init__(self, kwargs):
        self.name = kwargs["name"]
        self.description = kwargs["description"]
        self.rarity = kwargs["rarity"]
        self.value = kwargs["value"]
        self.effect = kwargs["effect"] if type(kwargs["effect"]) is list else [kwargs["effect"]]
        self.target = kwargs["target"]
        self.useSound = kwargs["useSound"]
        self.useVerb = kwargs["useVerb"]
        for effect in self.effect:
            if effect.name in ("recover", "refill", "restore") and self.target == "":
                self.target = "self"
                break
            if effect.name in ("damage", "drain", "destroy") and self.target == "":
                self.target = "enemy"
                break
        self.type = "consumable"

