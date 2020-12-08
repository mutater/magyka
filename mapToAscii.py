import numpy
from PIL import Image

def displayImage(imgSize = 912):
    gscale = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. "

    image = Image.open("map.png").convert('L')
    W, H = image.size[0], image.size[1]
    w = W/imgSize
    h = w/0.43
    r = int(H/h)
    aimg = []
    
    for j in range(r):
        y1 = int(j*h)
        y2 = int((j+1)*h)
        
        if j == r-1: y2 = H
        aimg.append("")
        
        for i in range(imgSize):
            x1 = int(i*w)
            x2 = int((i+1)*w)
            
            if i == imgSize-1: x2 = W
            
            img = image.crop((x1, y1, x2, y2))
            im = numpy.array(img)
            width, height = im.shape
            avg = int(numpy.average(im.reshape(width*height)))
            gsval = gscale[int((avg*(len(gscale)-1))/255)]
            aimg[j] += gsval
    
    string = aimg
    stringCols = len(string[0])
    for i in range(len(string) - 1, -1, -1):
        delete = True
        for character in gscale[:-1]:
            if character in string[i]:
                delete = False
                break
        if delete:
            string.pop(i)
    stringRows = len(string)
    with open("map.txt", "r+") as mapFile:
        mapFile.truncate(0)
        for line in string:
            mapFile.write(line + "\n")

displayImage()