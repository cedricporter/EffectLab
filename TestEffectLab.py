#!/usr/bin/env python
# author:  Hua Liang [ Stupid ET ]
# email:   et@everet.org
# website: http://EverET.org
#

import os, time, string, random
import autoreload
import ImageChops
from math import sqrt, sin, cos, tan, atan2
from EffectLab.Effect import *

Effect.empty_color = (255, 255, 255, 255)

def merge_origin_and_new(img, effect):
    '''Merge origin and new Image processed by function effect in one Image
    '''
    width, height = img.size 
    old = img
    # grid = GridMaker(20, 20) 
    # old = grid(img) 
    img = effect(old) 

    # merge origin and new image
    out = Image.new("RGBA", (width * 2, height))
    out.paste(old, (0, 0))
    out.paste(img, (width, 0)) 
    draw = ImageDraw.Draw(out) 
    draw.line((width, 0, width, height), (255, 0, 0, 255))

    return out

class Character(object):
    def __init__(self, img):
        self.width, self.height = img.size
        self.img = img

def main():
    print 'Started'

    effects = [
        LocalWarpEffect((50, 20), (80, 40), 30),
        RadianSqrtEffect(),
        LensWarpEffect(lambda x, y: (sign(x) * x ** 2, sign(y) * y ** 2)),
        RadianFormulaEffect(lambda r, phi: (r ** 2, phi), 4), 
        GlobalWaveEffect(),
        LensWarpEffect(lambda x, y: (sin(x * math.pi / 2), sin(y * math.pi / 2))),
        RadianFormulaEffect(lambda r, phi: (r ** 1.5 * math.cos(r), phi)),
               ] 

    # if os.path.exists('z.jpg'):
    #     img = Image.open('z.jpg')
    # else:
    #     img = Image.new("RGBA", (300, 300), (255, 255, 255, 255))

    characters = string.letters + string.digits
    char_img = {} 
    for ch in characters:
        img = Image.open('Images/%s.png' % ch)
        char_img[ch] = Character(img)

    text = ''.join(random.choice(string.letters) for i in xrange(4))

    img = Image.new("RGBA", (100, 40), (255, 255, 255, 255))
    font = ImageFont.truetype("UbuntuMono-R.ttf", 33)
    # draw = ImageDraw.Draw(img) 
    # draw.setfont(font) 
    # draw.text((10, 0), text, (0, 0, 0)) 

    last = random.choice(characters)
    offset = 15
    for i in range(5):
        ch = random.choice(characters)
        img.paste(char_img[ch].img,
                  (offset, 0),
                  ImageChops.invert(char_img[ch].img.split()[1]))
        last = ch
        offset += char_img[last].width - 1

    for index, effect in enumerate(effects):
        merge_origin_and_new(img, effect).save('%d.jpg' % index, quality=90)
        print '.',
    print 'done'

        
if __name__ == '__main__':
    autoreload.main(main)
