

class Settings:
    def __init__(self):
        self.defaultGame = False
        self.encounters = True if self.defaultGame else True
        self.craftCost = True if self.defaultGame else True
        self.purchaseCost = True if self.defaultGame else True
        self.godMode = False if self.defaultGame else False
        self.alwaysCounter = False if self.defaultGame else False
        
        self.sound = False
        self.moveBind = "esdf"
        self.interactBind = "a"


settings = Settings()
