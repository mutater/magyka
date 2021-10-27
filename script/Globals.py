import platform
import datetime

system = platform.system()
release = platform.release()

now = datetime.datetime.now()
runTime = now.strftime("%Y-%m-%d_%H-%M-%S")

stackableItems = ["consumable", "item", "modifier"]
slotList = ["weapon", "head", "chest", "legs", "acc 1", "acc 2"]
statList = ["attack", "armor", "strength", "intelligence", "vitality", "crit", "hit", "dodge", "max hp", "max mp"]
rarityList = ["garbage", "common", "uncommon", "rare", "epic", "legendary", "mythical"]

textSpeed = 0.03
