from script.Entity import Entity
import copy
import json
import os


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
                "x": 112,
                "y": 96,
            }),
            "enemy": None,
            "maps": {},
            "encounters": {},
            "stores": {},
            "quests": {},
            "recipes": [],
        }
        self.attributes.update(attributes)

    def get_player(self, attribute):
        """
        Gets an attribute from the player.

        Args:
            attribute:
                String key of attribute dict.

        Returns:
            Value of attribute dict.
        """

        return self.attributes["player"].attributes[attribute]

    def set_player(self, *args):
        """
        Sets a player attribute value.

        Args:
            *args:
                attribute, key, value
                or
                attribute, value

                attribute:
                    String key of attributes dict.
                key:
                    String key of attributes[attribute] dict.
                value:
                    The value to be set.
        """

        if len(args) == 3:
            self.attributes["player"].attributes[args[0]][args[1]] = args[2]
        else:
            self.attributes["player"].attributes[args[0]] = args[1]

    def get_enemy(self, attribute):
        """
        Gets an attribute from the enemy.

        Args:
            attribute:
                String key of attribute dict.

        Returns:
            Value of attribute dict.
        """

        return self.attributes["enemy"].attributes[attribute]

    def set_enemy(self, *args):
        """
        Sets a enemy attribute value.

        Args:
            *args:
                attribute, key, value
                or
                attribute, value

                attribute:
                    String key of attributes dict.
                key:
                    String key of attributes[attribute] dict.
                value:
                    The value to be set.
        """

        if len(args) == 3:
            self.attributes["enemy"].attributes[args[0]][args[1]] = args[2]
        else:
            self.attributes["enemy"].attributes[args[0]] = args[1]

    def save(self, backup=False):
        fileName = "saves/" + self.attributes["name"]
        if backup:
            fileName += " backup"
        fileName += ".json"

        with open(fileName, "w+") as saveFile:
            saveFile.write(json.dumps(self.export()))

    def export(self):
        attributes = copy.deepcopy(self.attributes)
        if self.attributes["player"]:
            attributes["player"] = attributes["player"].export()
        if self.attributes["enemy"]:
            attributes["enemy"] = attributes["enemy"].export()
        return attributes
