import sys
from script.Text import text


class Map:
    def __init__(self, attributes):
        self.attributes = {
            "tiles": [],
            "collision": [],
            "background": "0;0;0"
        }
        self.attributes.update(attributes)

    def get_tile(self, x, y):
        if x >= len(self.attributes["tiles"][0]) or x < 0:
            return self.attributes["background"]
        elif y >= len(self.attributes["tiles"]) or y < 0:
            return self.attributes["background"]
        else:
            return self.attributes["tiles"][y][x]

    def draw(self, playerX, playerY):
        mapWidth = min((text.width - text.oneThirdWidth - 2) // 2, 60)
        mapHeight = min(text.height - 2, 40)
        mapTop = 2 + (text.height - mapHeight - 2) // 2
        mapLeft = text.oneThirdWidth + 2 + (text.oneThirdWidth - mapWidth - 2) // 2

        if len(self.attributes["tiles"][0]) < mapWidth:
            mapWidth = len(self.attributes["tiles"][0])
        if len(self.attributes["tiles"]) < mapHeight:
            mapHeight = len(self.attributes["tiles"])

        top = playerY - mapHeight // 2
        bottom = playerY + mapHeight // 2
        left = playerX - mapWidth // 2
        right = playerX + mapWidth // 2

        if top < 0:
            top = 0
        if bottom > len(self.attributes["tiles"]):
            bottom = len(self.attributes["tiles"])
        if left < 0:
            left = 0
        if right > len(self.attributes["tiles"][0]):
            right = len(self.attributes["tiles"][0])

        mapText = ""

        for y in range(top, bottom):
            row = text.get_move_cursor(mapTop + y - top, mapLeft)

            for x in range(left, right):
                tile = self.get_tile(x, y)

                if x == playerX and y == playerY:
                    row += text.reset + "<>" + text.rgb(self.attributes["tiles"][y][x + 1], back=True)
                    continue

                if x > left and tile == self.attributes["tiles"][y][x - 1]:
                    row += "  "
                else:
                    row += text.rgb(tile, back=True) + "  "

            mapText += row
        sys.stdout.write(mapText)
        sys.stdout.flush()
