#!/usr/bin/env python
# author:  Hua Liang [ Stupid ET ]
# email:   et@everet.org
# website: http://EverET.org
#

import os
from EffectLab.Effect import *

def make_origin_and_new(img, effect):
    '''Merge origin and new Image processed by function effect in one Image
    '''
    width, height = img.size 
    grid = GridMaker(20, 20) 
    old = grid(img) 
    img = effect(old) 

    # merge origin and new image
    out = Image.new("RGBA", (width * 2, height))
    out.paste(old, (0, 0))
    out.paste(img, (width, 0)) 
    draw = ImageDraw.Draw(out) 

    draw.line((width, 0, width, height), (255, 0, 0, 255))

    return out

if __name__ == '__main__':
    effects = [GlobalWaveEffect(),
               RadianSqrtEffect(),
               RadianFormulaEffect(lambda r, phi: (r ** 1.5 * math.cos(r), phi)),
               LensWarpEffect(lambda x, y: (math.sin(x * math.pi / 2), math.sin(y * math.pi / 2))),
               LensWarpEffect(lambda x, y: (sign(x) * x ** 2, sign(y) * y ** 2)),
               RadianFormulaEffect(lambda r, phi: (r ** 2, phi), 4), 
               LocalWarpEffect((130, 120), (130, 50), 100),
               ]

    if os.path.exists('z.jpg'):
        img = Image.open('z.jpg')
    else:
        img = Image.new("RGBA", (300, 300), (255, 255, 255, 255))

    for index, effect in enumerate(effects):
        make_origin_and_new(img, effect).save('%d.jpg' % index, quality=90)
        print '.',
    print 'done'
