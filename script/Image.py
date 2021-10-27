from script.Mapper import mapper
from script.Text import text
import sys


class Image:
    """
    Image container.
    """
    def __init__(self, path, mode="image"):
        try:
            self.image = mapper.get_text(None, "image/" + path + ".png")
        except FileNotFoundError:
            self.image = [[""]]

        self.r = 1
        self.c = 1
        self.x = -1
        self.y = -1
        self.w = -1
        self.h = -1
        self.width = 0
        self.mode = mode
        
    def show(self, r=1, c=1, x=-1, y=-1, w=-1, h=-1, erase=False):
        """
        Shows or erases the image.

        Parameters:
            r:
                Integer row of top left corner.
            c:
                Integer column of top left corner.
            x:
                Integer offset of image from top left.
            y:
                Integer offset of image from top left.
            w:
                Integer width of image.
            h:
                Integer height of image.
            erase:
                Boolean; if True, replace pixels of image with background color and spaces.
        """

        if not self.image:
            return

        self.w = w
        self.h = h

        if w >= 0:
            width = w
        elif self.width:
            width = self.width
        else:
            width = len(self.image[0])

        if h >= 0:
            height = h
        else:
            height = len(self.image)

        left = x if x >= 0 else 0
        top = y if y >= 0 else 0

        if erase:
            print(text.reset)

        if self.mode == "image":
            for i in range(height):
                text.move_cursor(r + i, c)
                for j in range(width):
                    if self.image[i + top][j + left] == "000":
                        text.slide_cursor(0, 2)
                        continue

                    if erase:
                        print("  ")
                    else:
                        print(f'{text.rgb(self.image[i + top][j + left], back=True)}  ', end="")
        else:
            i = 0
            while i < len(self.image[0]):
                if i == width:
                    print("")

                if erase:
                    print(" ")
                else:
                    print(f'{text.c(self.image[i + top])}{self.image[i + top]}', end="")
        print(text.reset, end="")
        sys.stdout.flush()
    
    def show_at_description(self):
        self.show(text.height // 2 - 8, text.descriptionCenterCol - 16)
    
    def show_at_origin(self):
        self.show(1, 1)
    
    def show_description(self):
        self.show(1, 79)
