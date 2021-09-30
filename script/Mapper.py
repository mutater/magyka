from PIL import Image


class Mapper:
    """
    Generate 2d lists of text from images.
    """
    def __init__(self):
        """
        Initializes the class.
        """

        self.collision = {
            "ffffff": True,  # PASSABLE
            "000000": False  # IMPASSABLE
        }

    @staticmethod
    def get_text(colors, path):
        image = Image.open(path).convert('RGB')
        W, H = image.size[0], image.size[1]
        aimg = []
        
        for j in range(H):
            aimg.append([])
            for i in range(W):
                r, g, b = image.getpixel((i, j))
                hexCode = '%02x%02x%02x' % (r, g, b)
                rgb = f'{r};{g};{b}'
                if colors:
                    if hexCode in colors:
                        aimg[j].append(colors[hexCode])
                    else:
                        aimg[j].append(" ")
                else:
                    aimg[j].append(rgb)
        
        return aimg

    @staticmethod
    def test():
        image = Image.open("image/ansiColorIds.png").convert('RGB')
        W, H = image.size[0], image.size[1]
        counter = 0
        colorIdTable = {}
        
        for j in range(H):
            for i in range(W):
                r, g, b = image.getpixel((i, j))
                hexCode = '%02x%02x%02x' % (r, g, b)
                colorIdTable.update({hexCode: str(counter).rjust(3, "0")})
                counter += 1
        
        print(colorIdTable)


mapper = Mapper()
