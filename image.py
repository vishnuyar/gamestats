from PIL import Image, ImageDraw, ImageFont
import os
from game import Game
from connect import Connection

def createImage():
    # name of the file to save
    filename = "rank.png"
    fnt1 = ImageFont.truetype('Arial.ttf', 15)
    fnt = ImageFont.load_default()
    c = Connection()
    c.connect()
    g = Game(c)
    result = g.getRank()
    length = len(result)*25
    # create new image
    image = Image.new(mode = "RGB", size = (525,length), color = "#F4B41A")
    draw = ImageDraw.Draw(image)

    i = 10
    draw.text((200,5), text="LEADER BOARD", font=fnt1,align="middle", fill="#143D59")
    for r in result:
        # print(r)
        i+=20
        draw.text((10,i), text=" ".join(r), font=fnt, fill="#143D59")
        # i+=20
    image.save(filename)

# os.system(filename)
if __name__ == "__main__":
    createImage()