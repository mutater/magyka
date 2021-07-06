import platform

system = platform.system()
release = platform.release()

ansiEnabled = (system == "Windows" and release in ("8", "8.1", "10")) or system == "Linux"

stackableItems = ["consumable", "item", "modifier"]
slotList = ["weapon", "tome", "head", "chest", "legs", "accessory"]

statList = ["attack", "armor", "strength", "intelligence", "vitality", "crit", "hit", "dodge", "max hp", "max mp"]

textSpeed = 0.03
