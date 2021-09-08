from script.Logger import logger
from script.Text import text
import script.Globals as Globals


class Effect:
    """
    A runtime object created to hold the data for an effect used on an entity.
    
    Attributes
    ----------
    attributes : list
        table : str
            Constant, "effects"
        type : str
            The stat, hp, mp, etc. that the Effect affects
        value : int
            Strength of the Effect
        opp : str
            How the value of the effect is applied, "+", "*", and "="
        passive : list of Passive(s)
            Passives given when the Effect is applied
        crit : int
            The percent chance to deal double damage
        hit : int
            The percent chance to hit the target    
    
    Methods
    -------
    show_damage()
        Prints the heal and damage capabilities of the Effect.
    show_passive()
        Prints the passives applied by the Effect.
    show_stats()
        Prints the stats of the Effect.
    """
    
    def __init__(self, attributes):
        """
        Loads the effect's attributes.

        Parameters
        ----------
        attributes : list
            Variables that are meant to be saved
        """

        self.attributes = {
            "table": "effects",
            "type": "",
            "value": 0,
            "opp": "+",
            "passive": [],
            "crit": 4,
            "hit": 95
        }
        self.attributes.update(attributes)
    
    def show_damage(self):
        """
        Prints the heal and damage capabilities of the Effect.
        
        Returns
        -------
        None
        """
        
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
        
        text.slide_print(effectText, 0, 3)

    def show_stats(self):
        """
        Prints the stats of the Effect.
        
        Returns
        -------
        None
        """
        
        if self.attributes["type"] in Globals.statList:
            effectText = ""

            effectText += "+" if self.attributes["value"] > 0 else "-"
            effectText += self.attributes["type"].capitalize()

            if self.attributes["type"] == "max hp":
                effectText += " " + text.hp + text.reset
            elif self.attributes["type"] == "max mp":
                effectText += " " + text.mp + text.reset

            if self.attributes["opp"] == "*":
                effectText += str(abs(self.attributes["value"])) + "%"
            else:
                effectText += str(self.attributes["value"])

            if self.attributes["type"] in ("crit", "hit", "dodge"):
                effectText += " Chance"

            text.slide_print(effectText, 0, 4)

    def show_passive(self):
        """
        Prints the passives applied by the effect.

        Returns
        -------
        None
        """

        for passive in self.attributes["passive"]:
            passive.show_stats()


class Passive:
    """
    A runtime object created to hold the passive applied to an enemy or held by an effect.

    Attributes
    ----------
    attributes : list
        table : str
            Constant, "passives"
        name : str
            The display name
        description : str
            The description shown to the player
        buff : int
            Bool 1 or 0, 1 being a positive buff, 0 being a negative debuff
        turns : int
            The amount of turns the passive is applied
        effect : Effect
            The effect the passive applies per turn
        tags : dict
            Any extra information regarding the passive
    """

    def __init__(self, attributes):
        """
        Load the passive's attributes.

        Parameters
        ----------
        attributes : list
            Variables that are meant to be saved
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

        Parameters
        ----------
        turns : Bool
            Show the passive turns remaining after the name

        Returns
        -------
        str
        """

        effectColor = "light green" if self.attributes["buff"] else "light red"
        turnText = f' ({self.attributes["turns"]})' if turns else ""
        
        return text.c(effectColor) + self.attributes["name"] + text.reset + turnText
    
    def show_stats(self):
        """
        Prints the stats of the passive.

        Returns
        -------
        None
        """

        effectColor = "light green" if self.attributes["buff"] else "light red"
        
        if type(self.attributes["turns"]) is list:
            turnText = f'{self.attributes["turns"][0]} - {self.attributes["turns"][1]} turns'
        else:
            turnText = f'{self.attributes["turns"]} turn{"s" if self.attributes["turns"] > 1 else ""}'
        
        text.slide_cursor(0, 3)
        print(f'Applies {text.c(effectColor)}{self.attributes["name"]}{text.reset} for {turnText}')
