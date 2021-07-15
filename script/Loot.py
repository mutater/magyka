import json
import random
from script.BaseClass import BaseClass
from script.Item import Item
from script.Logger import logger
from script.Text import text
import script.Globals as Globals


class Loot(BaseClass):
    def __init__(self, attributes):
        self.defaults = {
            "table": "lootTables",
            "name": "Name",
            "drops": [],
            "xp": None,
            "gold": None,
            "mode": "normal",
            "tags": {}
        }
        
        super().__init__(attributes, self.defaults)
    
    def use(self):
        items = []
        for i in range(len(self.drops)):
            if random.randint(1, 100) <= self.drops[i][2]:
                if type(self.drops[i][1]) is list:
                    self.drops[i][1] = random.randint(self.drops[i][1][0], self.drops[i][1][1])
                items.append([self.drops[i][0], self.drops[i][1]])
        return items
    
    def export(self):
        for i in range(len(self.drops)):
            self.drops[i][0] = self.drops[i][0].export()
        return super().export()
