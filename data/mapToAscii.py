from PIL import Image

def displayImage():
    gscale = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. "
    colors = {
        # - DEBUG - #
        "000000": "@",
        # - PASSABLE - #
        "59c135": "=", # GRASS
        "9cdb43": ";", # LIGHT GRASS
        "d6f264": "-", # ARID LAND
        "fffc40": ">", # SAND
        "dae0ea": "$", # SNOW
        "4a5462": "+", # STONE
        # - IMPASSABLE - #
        "bb7547": "#", # MOUNTAIN
        "1a7a3e": "M", # TREE
        "143464": "8", # DEEP OCEAN
        "0d397b": "<", # OCEAN
        "154895": "~", # SHALLOW OCEAN
        "285cc4": ".", # SHORE OCEAN
        # - INTERACTABLE - #
        "b4202a": "T", # TOWN
        "9f9f9f": "o", # ENEMY
    }

    image = Image.open("Map.png").convert('RGB')
    W, H = image.size[0], image.size[1]
    aimg = []
    
    for j in range(H):
        aimg.append("")
        for i in range(W):
            r, g, b = image.getpixel((i, j))
            hex = '%02x%02x%02x' % (r, g, b)
            if hex in colors: aimg[j] += colors[hex]
            else: aimg[j] += " "

    with open("map/world map.txt", "r+") as mapFile:
        mapFile.truncate(0)
        for line in aimg:
            mapFile.write(line + "\n")
    
    return aimg
