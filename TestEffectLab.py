#!/usr/bin/env python
# author:  Hua Liang [ Stupid ET ]
# email:   et@everet.org
# website: http://EverET.org
#

import os, time, string, random
import autoreload
from math import sqrt, sin, cos, tan, atan2
from EffectLab.Effect import *

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


def main():
    print 'Started'

    effects = [
        RadianFormulaEffect(lambda r, phi: (r ** 2, phi), 4), 
        LensWarpEffect(lambda x, y: (sin(x * math.pi / 2), sin(y * math.pi / 2))),
        RadianFormulaEffect(lambda r, phi: (r ** 1.5 * math.cos(r), phi)),
        GlobalWaveEffect(),
        RadianSqrtEffect(),
        LensWarpEffect(lambda x, y: (sign(x) * x ** 2, sign(y) * y ** 2)),
        LocalWarpEffect((130, 120), (130, 50), 100),
               ] 

    # if os.path.exists('z.jpg'):
    #     img = Image.open('z.jpg')
    # else:
    #     img = Image.new("RGBA", (300, 300), (255, 255, 255, 255))

    text = ''.join(random.choice(string.letters) for i in xrange(4))

    img = Image.new("RGB", (100, 40), (255, 255, 255))
    font = ImageFont.truetype("UbuntuMono-R.ttf", 33)
    draw = ImageDraw.Draw(img) 
    draw.setfont(font)

    draw.text((10, 0), text, (0, 0, 0)) 
    del draw

    for index, effect in enumerate(effects):
        merge_origin_and_new(img, effect).save('%d.jpg' % index, quality=90)
        print '.',
    print 'done'

        
if __name__ == '__main__':
    autoreload.main(main)
