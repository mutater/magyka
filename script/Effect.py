from script.BaseClass import BaseClass
from script.Text import text
import script.Globals as Globals


class Effect(BaseClass):
    def __init__(self, attributes):
        self.defaults = {
            "type": "",
            "value": 0,
            "passive": None,
            "opp": "+",
            "attack": None,
            "values": []
        }
        
        super().__init__(attributes, self.defaults)
    
    def show_stats(self):
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
                hpDamageText = f'{text.red}{hpDamage[0]} - {hpDamage[1]}{"%" if hpMult else ""} ♥{text.reset}'
            else:
                hpDamageText = f'{text.red}{hpDamage}{"%" if hpMult else ""} ♥{text.reset}'
        if mpDamage:
            if type(mpDamage) is list:
                mpDamageText = f'{text.blue}{mpDamage[0]} - {mpDamage[1]}{"%" if mpMult else ""} ♦{text.reset}'
            else:
                mpDamageText = f'{text.blue}{mpDamage}{"%" if mpMult else ""} ♦{text.reset}'
        
        if attack:
            print(f' Damages {hpDamageText if hpDamageText else mpDamageText}')
        if heal:
            print(f' Heals {hpDamageText if hpDamageText else mpDamageText}')


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
            turnText = f'({self.turns})'
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
        
        print(f' Applies {text.c(effectColor)}{self.name}{text.reset} for {turnText}')
