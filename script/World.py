from script.Entity import Entity
import json


class World:
    """
    Holds all data for the world including loot, player, entities, etc.
    """

    def __init__(self, attributes):
        """
        Initializes the class.
        """

        self.attributes = {
            "name": "New World",
            "player": Entity({
                "location": "magyka",
                "x": 128,
                "y": 113,
            }),
            "enemy": None,
            "maps": {},
            "encounters": {},
            "stores": {},
            "quests": {},
            "recipes": [],
        }
        self.attributes.update(attributes)

    def save(self, backup=False):
        fileName = "saves/" + self.attributes["name"]
        if backup:
            fileName += " backup"
        fileName += ".json"

        with open(fileName, "w+") as saveFile:
            saveFile.write(json.dumps(self.export()))

    def export(self):
        attributes = self.attributes.copy()
        if self.attributes["player"]:
            attributes["player"] = attributes["player"].export()
        if self.attributes["enemy"]:
            attributes["enemy"] = attributes["enemy"].export()
        return attributes
