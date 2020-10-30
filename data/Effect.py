class Effect():
    def __init__(self, name, value):
        self.name = name
        self.value = value

class Heal(Effect):
    def __init__(self, name, value, operator):
        super().__init__(name, value)
        self.operator = operator

class Recover(Heal):
    def __init__(self, value, operator = "+"):
        super().__init__("recover", value, operator)

class Refill(Heal):
    def __init__(self, value, operator = "+"):
        super().__init__("refill", value, operator)

class Restore(Heal):
    def __init__(self, value, operator = ["+", "+"]):
        super().__init__("restore", value, operator)

class Attack(Effect):
    def __init__(self, name, value, crit, hit, dodge, resist):
        super().__init__(name, value)
        self.crit = crit
        self.hit = hit
        self.dodge = dodge
        self.resist = resist
        self.operator = "-"

class Damage(Attack):
    def __init__(self, value, crit, hit, dodge, resist = 1):
        super().__init__("damage", value, crit, hit, dodge, resist)

class Drain(Attack):
    def __init__(self, value, crit, hit, dodge, resist = 1):
        super().__init__("drain", value, crit, hit, dodge, resist)

class Destroy(Attack):
    def __init__(self, value, crit, hit, dodge, resist = [1, 1]):
        super().__init__("destroy", value, crit, hit, dodge, resist)

class Stat(Effect):
    def __init__(self, stat, value, operator = "+"):
        super().__init__("stat", value)
        self.stat = stat
        self.operator = operator

class Passive(Effect):
    def __init__(self, passive, value, hit, dodge, turns, target = "self"):
        super().__init__("passive", value if type(value) is list else [value])
        self.hit = hit
        self.dodge = dodge
        self.turns = turns
        self.passive = passive
        self.target = target