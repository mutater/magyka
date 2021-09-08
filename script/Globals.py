import platform
import datetime

system = platform.system()
release = platform.release()

now = datetime.datetime.now()
runTime = now.strftime("%Y-%m-%d_%H-%M-%S")

ansiEnabled = (system == "Windows" and release in ("8", "8.1", "10")) or system == "Linux"

stackableItems = ["consumable", "item", "modifier"]
slotList = ["weapon", "tome", "head", "chest", "legs", "acc 1", "acc 2"]
statList = ["attack", "armor", "strength", "intelligence", "vitality", "crit", "hit", "dodge", "max hp", "max mp"]

textSpeed = 0.03
