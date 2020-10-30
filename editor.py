from Magyka import clear, displayItem, command, options, c, reset, pressEnter
from data.Effect import *
import sys, keyboard, string, json, ast, copy, re

with open("data\\items.json", "r+") as itemFile:
    items = json.load(itemFile)
with open("data\\enemies.json", "r+") as enemyFile:
    enemies = json.load(enemyFile)
with open("data\\recipes.json", "r+") as recipeFile:
    recipes = json.load(recipeFile)

items.sort(key = lambda item : item["name"])
enemies.sort(key = lambda enemy : enemy["name"])
recipes.sort(key = lambda recipe : recipe["result"])

keyboard.press_and_release("windows + up")

selection = ""

hints = {
    "name": "String. Must be capitalized.",
    "description": "String.",
    "rarity": "String. Must be 'common', 'uncommon', 'rare', 'epic', 'legendary', or 'mythical'.",
    "value": "Integer. Must be positive or zero.",
    "slot": "String. Must be 'weapon', 'tome', 'head', 'chest', 'legs', 'feet', 'accessory'",
    "effect": "List of dictionaries. Arguments are 'type', 'name' (passives), 'value'[, 'passive', 'crit', 'hit', 'dodge', 'variance', 'resist']",
    "target": "String. Must be 'self', 'enemy'.",
    "mana": "Int. Only applies to tomes.",
    "attackName": "String. Only applies to tomes.",
    "attackSound": "String. Must be in the sounds folder.",
    "useSound": "String. Must be in the sounds folder.",
    "useVerb": "String.",
    "hp": "Integer.",
    "mp": "Integer.",
    "level": "List. [0] is the integer minimum level and [1] is the integer maximum level.",
    "stats": "Dictionary. 'statName': value",
    "gold": "Integer.",
    "xp": "Integer.",
    "items": "List of dictionaries. Each dict is composed of {'name', chance, quantity (range or integer)}.",
    "attackVerb": "String. Must be uncapitalized.",
    "magic": "List of dictionaries. Arguments are 'type', 'name' (passives), 'target', 'mana', 'attackSound', 'attackName', 'effect'[, 'passive', 'crit', 'hit', 'dodge', 'variance', 'resist']",
    "result": "String. Must be an existing item name.",
    "quantity": "Integer.",
    "ingredients": "List of lists. Each item is composed of ['name', quantity]."
}

def ifIn(key, container, backup):
    if key in container: return container[key]
    else: return backup

def main():
    global selection
    while 1:
        clear()
        print("\n -= Main =-")
        print("\n Choose a category to edit.")
        
        options(["Items", "Enemies", "Recipes"])
        option = command(False, "alphabetic", options = "ier", back = False)
        
        selection = option
        s_main()

# - ITEMS - #

def s_main():
    if selection == "i": global items
    if selection == "e": global enemies
    if selection == "r": global recipes
    page = 1
    while 1:
        clear()

        if selection == "i":
            print("\n -= Items =-\n")
            length = len(items)
        if selection == "e":
            print("\n -= Enemies =-\n")
            length = len(enemies)
        if selection == "r":
            print("\n -= Recipes =-\n")
            length = len(recipes)

        for i in range(-10 + 10*page, 10*page if 10*page < length else length):
            if selection == "i": print(f' {str(i)[:-1]}({str(i)[-1]}) {displayItem(items[i]["name"], items[i]["rarity"])}')
            if selection == "e": print(f' {str(i)[:-1]}({str(i)[-1]}) {enemies[i]["name"]}')
            if selection == "r": print(f' {str(i)[:-1]}({str(i)[-1]}) {recipes[i]["result"]}')

        next = False if length < page*10 + 1 else True
        previous = False if page == 1 else True

        options((["Next"] if next else []) + (["Previous"] if previous else []) + ["Create", "Save"])
        option = command(False, "optionumeric", options = ("n" if next else "") + ("p" if previous else "") + "".join(tuple(map(str, range(0, length)))) + "sc")

        if option in tuple(map(str, range(0, length))):
            s_inspect(int(option) + (page-1) * 10)
            if selection == "i": items.sort(key = lambda item : item["name"])
            if selection == "e": enemies.sort(key = lambda enemy : enemy["name"])
            if selection == "r": recipes.sort(key = lambda recipe : recipe["result"])
        elif option == "n" and next: page += 1
        elif option == "p" and previous: page -= 1
        elif option == "c": s_create()
        elif option == "s":
            if selection == "i":
                with open("data\\items.json", "w+") as itemFile:
                    json.dump(items, itemFile, indent = 2)
            if selection == "e":
                with open("data\\enemies.json", "w+") as enemyFile:
                    json.dump(enemies, enemyFile, indent = 2)
            if selection == "r":
                with open("data\\recipes.json", "w+") as recipeFile:
                    json.dump(recipes, recipeFile, indent = 2)
        elif option == "B": break

def s_inspect(index):
    if selection == "i": global items
    if selection == "e": global enemies
    if selection == "r": global recipes
    page = 1
    while 1:
        clear()
        if selection == "i":
            print(f'\n -= Inspect {items[index]["name"]} =-\n')
            parameters = [[key, items[index][key]] for key in items[index] if not key in ("type")]
            parameters.sort(key = lambda parameter : parameter[0])
        if selection == "e":
            print(f'\n -= Inspect {enemies[index]["name"]} =-\n')
            parameters = [[key, enemies[index][key]] for key in enemies[index]]
            parameters.sort(key = lambda parameter : parameter[0])
        if selection == "r":
            print(f'\n -= Inspect {recipes[index]["result"]} =-\n')
            parameters = [[key, recipes[index][key]] for key in recipes[index]]
            parameters.sort(key = lambda parameter : parameter[0])
        
        for i in range(-10 + 10*page, 10*page if 10*page < len(parameters) else len(parameters)):
            print(f' {str(i)[:-1]}({str(i)[-1]}) {parameters[i][0]}: {parameters[i][1]}')
        
        next = False if len(parameters) < page*10 + 1 else True
        previous = False if page == 1 else True
        
        options((["Next"] if next else []) + (["Previous"] if previous else []) + ["Copy", "Add", "Delete"])
        option = command(False, "optionumeric", options = ("n" if next else "") + ("p" if previous else "") + "".join(tuple(map(str, range(0, len(parameters))))) + "cad")
        
        if option in tuple(map(str, range(0, len(parameters)))):
            while 1:
                clear()
                option = int(option) + (page-1)*10
                
                print(f'\n -= Change {parameters[option][0]} =-')
                print(f'\n Current value: {parameters[option][1]}')
                print("\n " + hints[parameters[option][0]])

                value = command(True, "all", lower = False, prompt = str(parameters[option][1]))
                if re.match("[A-Za-z]", value): value = '"' + value + '"'
                if value == "B": break
                try: value = ast.literal_eval(value)
                except: break

                if selection == "i": items[index][parameters[option][0]] = value
                if selection == "e": enemies[index][parameters[option][0]] = value
                if selection == "r": recipes[index][parameters[option][0]] = value
                break
        elif option == "n" and next: page += 1
        elif option == "p" and previous: page -= 1
        elif option == "c":
            if selection == "i":
                copied = copy.deepcopy(items[index])
                copied["name"] += " - Copy"
                items.insert(index, copied)
            if selection == "e":
                copied = copy.deepcopy(enemies[index])
                copied["name"] += " - Copy"
                enemies.insert(index, copied)
            if selection == "r":
                copied = copy.deepcopy(recipes[index])
                copied["result"] += " - Copy"
                recipes.insert(index, copied)
        elif option == "a":
            while 1:
                clear()
                print("\n -= Add Parameter =-")
                print("\n Input parameter name:")

                name = command(True, "all", lower = False)
                if re.match("[A_Za-z]", name): name = '"' + name + '"'
                if name == "B": break
                try: name = ast.literal_eval(name)
                except: break

                print("\n Input parameter value:")
                print("\n " + ifIn(name, hints, "No hint."))

                value = command(True, "all", lower = False)
                if re.match("[A_Za-z]", value): value = '"' + value + '"'
                if value == "B": break
                try: value = ast.literal_eval(value)
                except: break

                if selection == "i": items[index][name] = value
                if selection == "e": enemies[index][name] = value
                if selection == "r": recipes[index][name] = value
                break
        elif option == "d":
            if selection == "i": items.pop(index)
            if selection == "e": enemies.pop(index)
            if selection == "r": recipes.pop(index)
            break
        elif option == "B": break

def s_create():
    if selection == "i": global items
    if selection == "e": global enemies
    if selection == "r": global recipes
    while 1:
        clear()
        if selection == "i":
            print("\n -= Create Item =-")
        
            options(["Item", "Equipment", "Consumable"])
            option = command(options = "iec")
            
            if option == "B": break
            elif option == "i":
                parameters = ["name", "description", "rarity", "value"]
                inputParameters = {"type": "item"}
            elif option == "e":
                parameters = ["name", "description", "rarity", "value", "slot", "effect", "mana", "attackName", "attackSound"]
                inputParameters = {"type": "equipment"}
            elif option == "c":
                parameters = ["name", "description", "rarity", "value", "effect", "target", "useSound", "useVerb"]
                inputParameters = {"type": "consumable"}
        if selection == "e":
            parameters = ["name", "hp", "mp", "level", "stats", "gold", "xp", "items", "attackSound", "attackVerb"]
            inputParameters = {}
        if selection == "r":
            parameters = ["result", "quantity", "ingredients"]
            inputParameters = {}

        parameters.sort()

        broken = False
        for i in range(len(parameters)):
            print(f'\n {parameters[i]}: ')
            print(" " + hints[parameters[i]])
            
            inputParameters.update({parameters[i]: command(True, "all", lower = False)})
            if inputParameters[parameters[i]] == "": inputParameters.pop(parameters[i])
            elif inputParameters[parameters[i]] == "B":
                broken = True
                break
            try: inputParameters[parameters[i]] = ast.literal_eval(inputParameters[parameters[i]])
            except: pass
            if parameters[i] == "effect" and not type(inputParameters[parameters[i]]) is list: inputParameters[parameters[i]] = [inputParameters[parameters[i]]]
        if broken: break
        
        if selection == "i":
            items.append(inputParameters)
            items.sort(key = lambda item : item["name"])
        if selection == "e":
            enemies.append(inputParameters)
            enemies.sort(key = lambda enemy : enemy["name"])
        if selection == "r":
            recipes.append(inputParameters)
            recipes.sort(key = lambda recipe : recipe["result"])
        
        break

main()