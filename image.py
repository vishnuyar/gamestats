from PIL import Image, ImageDraw, ImageFont
import os
from game import Game
from connect import Connection

def createImage(args):
    # name of the file to save
    filename = "rank.png"
    fnt1 = ImageFont.truetype('Arial.ttf', 15)
    fnt = ImageFont.load_default()
    c = Connection()
    c.connect()
    g = Game(c)
    lastNgames = None
    if args:
        lastNgames = args[0]
    result = g.getRank(lastNgames)
    length = len(result)*25
    # create new image
    image = Image.new(mode = "RGB", size = (525,length), color = "#EDF5E1")
    draw = ImageDraw.Draw(image)
    # #143D59,#F4B41A #EDF5E1 0B0C10 #EEE2DC #AC3B61 #25274D #29648A
    i = 10
    if lastNgames:
        text = f"LEADER BOARD - Last {lastNgames} Games"
        draw.text((175,5), text=text, font=fnt1,align="middle", fill="#143D59")
    else:
        text = "LEADER BOARD"
        draw.text((200,5), text=text, font=fnt1,align="middle", fill="#143D59")
    for r in result:
        # print(r)
        i+=20
        draw.text((10,i), text=" ".join(r), font=fnt, fill="#0B0C10")
        # i+=20
    image.save(filename)

# os.system(filename)
if __name__ == "__main__":
    createImage()