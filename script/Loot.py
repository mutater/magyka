import random


class Loot:
    """
    A loot table.
    """
    def __init__(self, attributes):
        """
        Initializes the class.

        Parameters:
            attributes:
                Dictionary of class attributes.

                table:
                    String constant ("lootTables").
                name:
                    String.
                drops:
                    List of lists of droppable items.

                    drops = [
                        [name, quantity, chance],
                    ]
                xp:
                    Integer amount of xp dropped.
                gold:
                    Integer amount of gold dropped.
                mode:
                    String type of drop mode.

                    "normal" means each item is randomly chosen to drop.
                tags:
                    Dict of any extra information.
        """

        self.attributes = {
            "table": "lootTables",
            "name": "Name",
            "drops": [],
            "xp": None,
            "gold": None,
            "mode": "normal",
            "tags": {}
        }
        self.attributes.update(attributes)
    
    def use(self):
        """
        Generates a list of items.

        Returns:
            List of [item, quantity] lists.
        """

        items = []
        for i in range(len(self.attributes["drops"])):
            if random.randint(1, 100) <= self.attributes["drops"][i][2]:
                if type(self.attributes["drops"][i][0]) is list:
                    self.attributes["drops"][i][1] = random.randint(
                        self.attributes["drops"][i][1][0],
                        self.attributes["drops"][i][1][1]
                    )
                else:
                    self.attributes["drops"][i][0] = self.attributes["drops"][i][0][
                        random.randint(0, len(self.attributes["drops"][i][0]) - 1)
                    ]
                items.append([self.attributes["drops"][i][0], self.attributes["drops"][i][1]])
        return items
