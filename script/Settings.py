

class Settings:
    """
    Holds settings for playing the game. Can be edited.
    """

    def __init__(self):
        """
        Initializes the class.
        """

        self.defaultGame = False  # Enables the Default game mode.

        self.encounters = True if self.defaultGame else True  # Random encounters.
        self.craftCost = True if self.defaultGame else True  # Consume ingredients when crafting.
        self.purchaseCost = True if self.defaultGame else True  # Consume gold when purchasing.
        self.godMode = False if self.defaultGame else False  # Take damage.
        self.alwaysCounter = False if self.defaultGame else False  # Always counter when guarding.
        
        self.sound = False  # In game sound.
        self.moveBind = "esdf"  # The keys to navigate pages and the map.
        self.interactBind = "a"  # The key to interact on the map.


settings = Settings()
