from script.BaseClass import BaseClass
from script.Logger import logger
from script.Text import text
import script.Globals as Globals


class Effect(BaseClass):
    def __init__(self, attributes):
        self.defaults = {
            "type": "",
            "value": 0,
            "passive": [],
            "opp": "+",
            "attack": None,
            "values": [],
            "crit": 4,
            "hit": 95,
            "dodge": 1
        }
        
        super().__init__(attributes, self.defaults)
    
    def show_stats(self, damage=True, stats=True, passive=True):
        # Printing healing/ damage
        if damage:
            hpDamage, hpDamageText, hpMult = 0, "", False
            mpDamage, mpDamageText, mpMult = 0, "", False
            
            if self.type in ("damageHp", "damageMp", "attack"):
                attack = True
            else:
                attack = False
            if self.type in ("healHp", "healMp"):
                heal = True
            else:
                heal = False
            
            for stat in ("healHp", "healMp", "damageHp", "damageMp"):
                if self.type == stat:
                    if "Hp" in stat:
                        hpDamage = self.value
                        hpMult = self.opp == "*"
                    else:
                        mpDamage = self.value
                        mpMult = self.opp == "*"
            
            if self.type == "attack" and type(self.value) is list:
                hpDamage = self.value
                hpMult = False
            
            if hpDamage:
                if type(hpDamage) is list:
                    hpDamageText = f'{hpDamage[0]} - {hpDamage[1]}{"%" if hpMult else ""} {text.hp}{text.reset}'
                else:
                    hpDamageText = f'{hpDamage}{"%" if hpMult else ""} {text.hp}{text.reset}'
            if mpDamage:
                if type(mpDamage) is list:
                    mpDamageText = f'{mpDamage[0]} - {mpDamage[1]}{"%" if mpMult else ""} {text.mp}{text.reset}'
                else:
                    mpDamageText = f'{mpDamage}{"%" if mpMult else ""} {text.mp}{text.reset}'
            
            if attack:
                text.slide_cursor(0, 3)
                print(f'Damages {hpDamageText if hpDamageText else mpDamageText}')
            if heal:
                text.slide_cursor(0, 3)
                print(f'Heals {hpDamageText if hpDamageText else mpDamageText}')
        
        # Printing stats
        if stats:
            color, character = "", ""
            statList = ("max hp", "max mp", "armor", "strength", "intelligence", "vitality")
            
            if self.type == "attack" and type(self.value) is not list:
                text.slide_cursor(0, 3)
                if self.opp == "*":
                    print(f'{abs(self.value)}% {"Increased" if self.value > 0 else "Decreased"} Attack')
                else:
                    print(f'{"+" if self.value > 0 else "-"}{self.value} Attack')
            if self.type in statList:
                if self.type == "max hp":
                    symbol = " " + text.hp
                elif self.type == "max mp":
                    symbol = " " + text.mp
                else:
                    symbol = ""
                
                text.slide_cursor(0, 3)
                if self.opp == "*":
                    print(f'{abs(self.value)}% {"Increased" if self.value > 0 else "Decreased"} {self.type.capitalize()}{symbol}{text.reset}')
                else:
                    print(f' {"+" if self.value > 0 else ""}{self.value} {self.type.capitalize()}{symbol}{text.reset}')
            elif self.type in ("crit", "hit", "dodge"):
                text.slide_cursor(0, 3)
                print(f'{abs(self.value)}% {"Increased" if self.value > 0 else "Decreased"} {self.type.capitalize()} Chance')
        
        # Printing passives
        if passive:
            for passive in self.passive:
                passive.show_stats()
    
    def export(self):
        for i in range(len(self.passive)):
            self.passive[i] = self.passive[i].export()
        return super().export()


class Passive(BaseClass):
    def __init__(self, attributes):
        self.defaults = {
            "name": "Name",
            "description": "Description",
            "buff": 0,
            "turns": 1,
            "effect": [],
            "tags": {}
        }
        
        super().__init__(attributes, self.defaults)
    
    def get_name(self, turns=False):
        if self.buff:
            effectColor = "light green"
        else:
            effectColor = "light red"
        
        if turns:
            turnText = f' ({self.turns})'
        else:
            turnText = ""
        
        return text.c(effectColor) + self.name + text.reset + turnText
    
    def show_stats(self):
        if self.buff:
            effectColor = "light green"
        else:
            effectColor = "light red"
        
        if type(self.turns) is list:
            turnText = f'{self.turns[0]} - {self.turns[1]} turns'
        else:
            turnText = f'{self.turns} turn{"s" if self.turns > 1 else ""}'
        
        text.slide_cursor(0, 3)
        print(f'Applies {text.c(effectColor)}{self.name}{text.reset} for {turnText}')
    
    def export(self):
        for i in range(len(self.effect)):
            self.effect[i] = self.effect[i].export()
        return super().export()
