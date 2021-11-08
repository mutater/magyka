import copy

from script.Control import control
from script.Text import text
import script.Globals as Globals


class Effect:
    """
    The damage, healing, or stat changes of an item, equipment, or attack.
    """
    
    def __init__(self, attributes):
        """
        Loads the effect's attributes.

        Args:
            attributes:
                Dictionary of class attributes.

                table:
                    String constant ("effects").
                type:
                    String stat (hp, mp, etc.) that the Effect affects.
                stat:
                    String name of stat affected if type is "Stat".
                value:
                    Integer strength of the Effect.
                opp:
                    String value of how the Effect is applied ("+", "*", "=").
                passive:
                    List of Passives given when the Effect is applied.
                crit:
                    Integer percent chance to deal increased damage.
                hit:
                    Integer percent chance to hit the target.
        """

        self.attributes = {
            "table": "effects",
            "type": "",
            "stat": "",
            "value": 0,
            "opp": "+",
            "passive": [],
            "crit": 4,
            "hit": 95
        }
        self.attributes.update(attributes)
    
    def show_damage(self):
        if self.attributes["type"] not in ("hp", "mp", "attack"):
            return
        
        if type(self.attributes["value"]) is list:
            effectText = f'{self.attributes["value"][0]} - {self.attributes["value"][1]}'
        else:
            effectText = f'{self.attributes["value"]}'

        if self.attributes["opp"] == "*":
            effectText += "%"
        
        if self.attributes["type"] == "hp":
            effectText += text.hp + text.reset
        if self.attributes["type"] == "mp":
            effectText += text.mp + text.reset
        
        if self.attributes["type"] in ("-hp", "-mp", "attack"):
            effectText = "Damages " + effectText
        if self.attributes["type"] in ("+hp", "-hp"):
            effectText = "Heals " + effectText

        text.slide_cursor(0, 3)
        print(effectText)

    def show_stats(self):
        if self.attributes["type"] in Globals.statList and self.attributes["type"] != "attack":
            effectText = ""

            effectText += "+ " if self.attributes["value"] > 0 else "- "

            if self.attributes["opp"] == "*":
                effectText += str(abs(self.attributes["value"])) + "%"
            else:
                effectText += str(self.attributes["value"])

            if self.attributes["type"] == "max hp":
                effectText += " " + text.hp + text.reset
            elif self.attributes["type"] == "max mp":
                effectText += " " + text.mp + text.reset

            effectText += " " + self.attributes["type"].capitalize()

            if self.attributes["type"] in ("crit", "hit", "dodge"):
                effectText += " Chance"

            text.slide_cursor(0, 4)
            print(effectText)

    def show_passive(self):
        for passive in self.attributes["passive"]:
            passive.show_stats()

    def export(self):
        attributes = copy.deepcopy(self.attributes)

        for i in range(len(attributes["passive"])):
            attributes["passive"][i] = attributes["passive"][i].export()

        return attributes


class Passive:
    """
    A passive applied to an Entity or Effect.
    """

    def __init__(self, attributes):
        """
        Initializes the class and loads its attributes.

        Parameters:
            attributes:
                Dictionary of class attributes.

                table:
                    String constant ("passives").
                name:
                    String display name.
                description
                    String display description.
                buff:
                    Integer 1 or 0, 1 being a buff, 0 being a debuff.
                turns:
                    Integer number of turns the passive is applied.
                effect:
                    Effect the passive applies.
                tags:
                    Dict of any extra information.
        """

        self.attributes = {
            "table": "passives",
            "name": "Name",
            "description": "Description",
            "buff": 0,
            "turns": 1,
            "effect": [],
            "tags": {}
        }
        self.attributes.update(attributes)
    
    def get_name(self, turns=False):
        """
        Returns the name of the passive.

        Parameters:
            turns:
                Boolean; if True, append turn count to display name.

        Returns:
            String colored display name.
        """

        effectColor = "light green" if self.attributes["buff"] else "light red"
        turnText = f' ({self.attributes["turns"]})' if turns else ""
        
        return text.c(effectColor) + self.attributes["name"] + text.reset + turnText
    
    def show_stats(self):
        effectColor = "light green" if self.attributes["buff"] else "light red"
        
        if type(self.attributes["turns"]) is list:
            turnText = f'{self.attributes["turns"][0]} - {self.attributes["turns"][1]} turns'
        else:
            turnText = f'{self.attributes["turns"]} turn{"s" if self.attributes["turns"] > 1 else ""}'
        
        text.slide_cursor(0, 3)
        print(f'Applies {text.c(effectColor)}{self.attributes["name"]}{text.reset} for {turnText}')

    def export(self):
        attributes = copy.deepcopy(self.attributes)

        for i in range(len(attributes["effect"])):
            attributes["effect"][i] = attributes["effect"][i].export()

        return attributes
