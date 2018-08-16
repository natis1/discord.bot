#!/usr/bin/env python

import os
from distutils.util import strtobool as sbool

from PIL import Image

ImageUrls = {
    "A": "https://i.imgur.com/pe0o9M7.png",
    "B": "https://i.imgur.com/HDX1INg.png",
    "C": "https://i.imgur.com/NWYdpyt.png",
    "D": "https://cdn.discordapp.com/attachments/417434015554076672/417434518543269890/unknown.png",
    "E": "https://cdn.discordapp.com/attachments/417434015554076672/417434554786381835/unknown.png",
    "F": "https://cdn.discordapp.com/attachments/417434015554076672/417434590974836736/unknown.png",
    "G": "https://cdn.discordapp.com/attachments/417434015554076672/417434617767788544/unknown.png",
    "H": "https://i.imgur.com/3NNkHnF.png",
    "I": "https://cdn.discordapp.com/attachments/417434015554076672/417434779584167970/unknown.png",
    "J": "https://cdn.discordapp.com/attachments/417434015554076672/417435048309161996/unknown.png",
    "K": "https://i.imgur.com/EpwTb1V.png",
    "L": "https://cdn.discordapp.com/attachments/417434015554076672/417435402475929620/cA9VIKY.png",
    "M": "https://cdn.discordapp.com/attachments/417434015554076672/417435505974837264/1usEdyV.png",
    "N": "https://cdn.discordapp.com/attachments/417434015554076672/417435608475238400/unknown.png",
    "O": "https://i.imgur.com/dKDvJ3j.png",
    "P": "https://i.imgur.com/BRZLizo.png",
    "Q": "https://cdn.discordapp.com/attachments/417434015554076672/417435991301685250/unknown.png",
    "R": "https://i.imgur.com/JVAbnYM.png",
    "S": "https://cdn.discordapp.com/attachments/417434015554076672/417436105588080640/unknown.png",
    "T": "https://i.imgur.com/4mXkMwk.png",
    "U": "https://cdn.discordapp.com/attachments/417434015554076672/417436239763996674/unknown.png",
    "V": "https://cdn.discordapp.com/attachments/417434015554076672/417436505989185553/unknown.png",
    "W": "https://cdn.discordapp.com/attachments/417434015554076672/417436720200417280/uObt2pe.png",
    "X": "https://cdn.discordapp.com/attachments/417434015554076672/417437103262007298/bAWB5aW.png",
    "Y": "https://cdn.discordapp.com/attachments/417434015554076672/417437262977171460/unknown.png",
    "Z": "https://cdn.discordapp.com/attachments/417434015554076672/417437447702577152/unknown.png",
    "?": "https://cdn.discordapp.com/attachments/297468195026239489/418276386755837953/unknown.png",
    ".": "https://cdn.discordapp.com/attachments/297468195026239489/418285079505272852/unknown.png",
    "'": "https://cdn.discordapp.com/attachments/297468195026239489/418277293014777858/unknown.png",
    ",": "https://cdn.discordapp.com/attachments/297468195026239489/418281643195891722/unknown.png",
    "0": "https://cdn.discordapp.com/attachments/410556297046523905/418286483565182976/0.png",
    "1": "https://cdn.discordapp.com/attachments/410556297046523905/418286497687404555/1.png",
    "2": "https://cdn.discordapp.com/attachments/410556297046523905/418286508299124748/2.png",
    "3": "https://cdn.discordapp.com/attachments/410556297046523905/418286519707631636/3.png",
    "4": "https://cdn.discordapp.com/attachments/410556297046523905/418286534119391232/4.png",
    "5": "https://cdn.discordapp.com/attachments/410556297046523905/418286548140687361/5.png",
    "6": "https://cdn.discordapp.com/attachments/410556297046523905/418286559138414593/6.png",
    "7": "https://cdn.discordapp.com/attachments/410556297046523905/418286571846893568/7.png",
    "8": "https://cdn.discordapp.com/attachments/410556297046523905/418286582819192834/8.png",
    "9": "https://cdn.discordapp.com/attachments/410556297046523905/418286599332429844/9.png",
    '"': "https://cdn.discordapp.com/attachments/297468195026239489/418298833622007808/udungo.png",
}

excludeChars = {"?": "questionMark", "'": "apostrophe", ".": "periodDot", ",": "comma"}

excludeReverse = {v: k for k, v in excludeChars.items()}

# if not os.path.exists("Images"):
#    if not os.path.exists("Images"): os.makedirs("Images")
#    for letter, url in ImageUrls.items():
#        with open(os.path.join("Images",
#  letter if letter not in excludeChars.keys() else excludeChars[letter]), 'wb') as file:
#            res = get(url)
#            file.write(res.content)
#

Images = {
    filename
    if filename not in excludeReverse.keys()
    else excludeReverse[filename]: Image.open(
        open(os.path.join("Images", filename), "rb")
    )
    for filename in os.listdir("Images")
}


def create_image(text, to_scale=False):
    global Images

    m = Image.new("RGBA", (9000, 30000), (0, 0, 0, 0))  # transparent background
    offset = max_y = max_x = y = j = 0

    def scale(img):
        width = 100
        widthpercent = width / float(img.size[0])
        hsize = int((float(img.size[1]) * float(widthpercent)))
        img = img.resize((width, hsize), Image.BICUBIC)
        return img

    def newline():
        nonlocal y, j, offset
        y += 180
        j = offset = 0

    def space():
        nonlocal offset
        offset += 60

    if to_scale is True:
        Images = {letter: scale(img) for letter, img in Images.items()}

    for i in text.upper():
        if i != " " and i not in Images.keys():
            continue

        if (i == " " and j % 40 >= 30) or (j >= 40):
            newline()
            continue

        if i == " ":
            space()
            continue

        m.paste(Images[i], (offset, y))
        offset += Images[i].size[0]
        max_y = max(Images[i].size[1], max_y)
        j += 1

        max_x = max(max_x, offset)

    m = m.crop((0, 0, max_x, max_y if max_y > y else y + max_y))
    return m


def create_image_file(text, file_name):
    create_image(text, True).save(file_name)


if __name__ == "__main__":
    scaling = None
    while not (scaling is True or scaling is False):
        # noinspection PyBroadException
        try:
            scaling = bool(sbool(input("Scale letters up?: ")))
        except Exception:
            pass
    fname = input("Save file as (needs file extension): ")
    create_image(input("Enter word to convert: "), to_scale=scaling).save(str(fname))
