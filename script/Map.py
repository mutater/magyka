import sys
from script.Text import text


class Map:
    """
    Holds the data for a single map including tiles and Entities.
    """

    def __init__(self, attributes):
        """

        Args:
            attributes:
                tiles:
                    List of rows, which are each lists of String tiles. Contains the visuals for the map.

                    e.g. a 2x2 map could be [["0;0;0", "0;0;0"], ["0;0;0", "0;0;0"]]
                collision:
                    List of rows, which are each lists of String tiles. Contains the collision for the map.

                    same format as tiles.
                background:
                    String background color. "r;g;b".
        """

        self.attributes = {
            "tiles": [],
            "collision": [],
            "background": "0;95;255"
        }
        self.attributes.update(attributes)

    def get_tile(self, x, y):
        """
        Loads a tile from int x and y position.

        Args:
            x:
                Int tile location in x axis.
            y:
                Int tile location in y axis.

        Returns:
            String tile, "r;g;b".
        """

        if x >= len(self.attributes["tiles"][0]) or x < 0:
            return self.attributes["background"]
        if y >= len(self.attributes["tiles"]) or y < 0:
            return self.attributes["background"]
        if self.attributes["tiles"][y][x] == "255;0;255":
            return self.attributes["background"]

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

        """if top < 0:
            top = 0
        if bottom > len(self.attributes["tiles"]):
            bottom = len(self.attributes["tiles"])
        if left < 0:
            left = 0
        if right > len(self.attributes["tiles"][0]):
            right = len(self.attributes["tiles"][0])"""

        mapText = ""

        for y in range(top, bottom):
            row = text.get_move_cursor(mapTop + y - top, mapLeft)

            for x in range(left, right):
                tile = self.get_tile(x, y)

                if x == playerX and y == playerY:
                    row += text.reset + "<>" + text.rgb(self.get_tile(x + 1, y), back=True)
                    continue

                if x > left and tile == self.get_tile(x - 1, y):
                    row += "  "
                else:
                    row += text.rgb(tile, back=True) + "  "

            mapText += row
        sys.stdout.write(mapText)
        sys.stdout.flush()
