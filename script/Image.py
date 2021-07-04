import script.Globals as Globals
from script.Mapper import mapper
from script.Text import text


class Image:
    def __init__(self, path, mode="image"):
        try:
            self.image = mapper.get_text(mapper.imageColors, "image/" + path + ".png")
        except:
            self.image = [[""]]
        self.r = 1
        self.c = 1
        self.x = -1
        self.y = -1
        self.w = -1
        self.h = -1
        self.width = 0
        self.mode = mode
        
    def show(self, r=1, c=1, x=-1, y=-1, w=-1, h=-1):
        if not self.image:
            return
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        if x >= 0:
            left = x
        else:
            left = 0
        if y >= 0:
            top = y
        else:
            top = 0
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
        
        if self.mode == "image":
            for i in range(height):
                text.move_cursor(r + i, c)
                for j in range(width):
                    if self.image[i + top][j + left] == "000":
                        text.slide_cursor(0, 2)
                        continue
                    print(f'{text.c(self.image[i + top][j + left], back=True, code=True)}  ', end="")
        else:
            i = 0
            while i < len(self.image[0]):
                if i == width:
                    print("")
                print(f'{text.c(self.image[i + top])}{self.image[i + top]}', end="")
        print(text.reset, end="")
    
    def show_at_description(self):
        self.show(7, 85)
    
    def show_at_origin(self):
        self.show(1, 1)
    
    def erase(self):
        if not self.image:
            return
        if self.x >= 0:
            left = self.x
        else:
            left = 0
        if self.y >= 0:
            top = self.y
        else:
            top = 0
        if self.w >= 0:
            width = self.w
        elif self.width:
            width = self.width
        else:
            width = len(self.image[0])
        if self.h >= 0:
            height = self.h
        else:
            height = len(self.image)
        
        if self.mode == "image":
            for i in range(height):
                text.move_cursor(r + i, c)
                for j in range(width):
                    print(f'{text.reset}{"  " if self.mode == "image" else " "}', end="")
        else:
            i = 0
            print(text.reset, end="")
            while i < len(self.image[0]):
                if width % i == 0:
                    print("")
                print(f' {self.image[i + top]}', end="")
        print(text.reset, end="")
