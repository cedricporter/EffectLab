#!/usr/bin/env python
# author:  Hua Liang [ Stupid ET ]
# email:   et@everet.org
# website: http://EverET.org
#
# This is a tools that generate each image of character

import random, string, md5, time
import Image, ImageDraw, ImageFont
import StringIO, string

def get_vertical_map(img):
    img = img.convert('L') 
    # segmentation
    m = [0] * width 
    for x in range(width):
        for y in range(height):
            if img.getpixel((x, y)) != 255:
                m[x] += 1
    return m

def get_character_region(iterator):
    '''get character region
    '''
    state = "empty"

    i, lbd, rbd = 0, -1, -1
    while True:
        data = iterator.next() 
        if state == "empty":
            if data != 0:
                # enter
                state = "collect"
                lbd = i
        elif state == "collect":
            if data == 0:
                # leave
                rbd = i
                state = "empty"
                yield (lbd, rbd)
        i += 1

width, height = 1200, 40

characters = string.letters + string.digits

# draw img
img = Image.new("RGBA", (width, height), (255, 255, 255, 0))
font = ImageFont.truetype("../UbuntuMono-R.ttf", 33)
draw = ImageDraw.Draw(img) 
draw.setfont(font)
draw.text((10, 0), characters, (0, 0, 0, 255)) 
del draw

m = get_vertical_map(img)

for index, bd in enumerate(get_character_region(iter(m))):
    ch = characters[index]

    img.crop((bd[0], 0, bd[1], height)).save('../Images/%s.png' % ch) 

