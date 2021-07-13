

class Settings:
    def __init__(self):
        self.defaultGame = True
        self.encounters = True if self.defaultGame else False
        self.encounterChanceHuntTrue = 5
        self.encounterChanceHuntFalse = 0.5
        self.craftCost = True if self.defaultGame else False
        self.buyCost = True if self.defaultGame else False
        self.godMode = False if self.defaultGame else True


settings = Settings()
