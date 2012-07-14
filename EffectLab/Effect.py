#!/usr/bin/env python
# author:  Hua Liang [ Stupid ET ]
# email:   et@everet.org
# website: http://EverET.org
#

import random, string, md5, time
import Image, ImageDraw, ImageFont, ImageChops, ImageFilter
import StringIO
import math, operator

# Filters that input Image and output Image
#

class Effect(object):
    '''The base Effect
    All Effects have a member function called "filter"
    which receives a PIL Image and return a PIL Image
    '''
    name = 'Base Effect'
    empty_color = (128, 128, 128, 255)
    def __init__(self):
        pass

    def __call__(self, img):
        '''The effect can act like a filter function'''
        return self.filter(img)

    def filter(self, img):
        return img


class GlobalWarpEffect(Effect):
    '''Warping Effect Base class.
    provide basic warping framework
    '''
    name = 'Warp Effect' 

    def __init__(self, formula, antialias=2):
        self.formula = formula
        self.antialias = antialias

    def filter(self, img):
        '''Effect Kernel of radius based Effect. 
        @param formula is a function like f(x, y) => (x', y'), -1 <= x <= 1 and -1 <= y <= 1
        '''
        width, height = img.size
        nx, ny = width, height
        new_img = img.copy()
        nband = len(img.getpixel((0, 0)))
        for j in range(height):
            for i in range(width):
                found = 0
                psum = (0, ) * nband
                new_img.putpixel((i, j), Effect.empty_color)
                # antialias
                for ai in range(self.antialias):
                    x = 2 * (i + ai / float(self.antialias)) / width - 1
                    for aj in range(self.antialias):
                        y = 2 * (j + aj / float(self.antialias)) / height - 1

                        # distortion 
                        xnew, ynew = self.formula(x, y) 

                        i2 = int(round(0.5 * nx * (xnew + 1)))
                        j2 = int(round(0.5 * ny * (ynew + 1)))

                        if not (0 <= i2 < nx and 0 <= j2 < ny):
                            continue

                        pt = img.getpixel((i2, j2))
                        psum = map(operator.add, psum, pt)
                        found += 1 

                if found > 0:
                    psum = map(operator.div, psum, (self.antialias * self.antialias, ) * len(psum)) 
                    new_img.putpixel((i, j), tuple(psum))

        return new_img


class RadianFormulaEffect(Effect):
    '''Transform the Image according to the input formula
    @note The formula is a function like f(r, phi) => (r, phi)
    which r is radius and phi is radian angel.
    ''' 
    name = 'Radian Formula Effect'

    def __init__(self, formula, antialias=2):
        self.formula = formula
        self.antialias = antialias

    def filter(self, img):
        def radian_formula(x, y):
            '''transform formula
            func is a function that like f(r, phi) => (r, phi)
            '''
            r = math.sqrt(x ** 2 + y ** 2)
            phi = math.atan2(y, x)

            r, phi = self.formula(r, phi)

            xnew = r * math.cos(phi)
            ynew = r * math.sin(phi)

            return xnew, ynew

        warp = GlobalWarpEffect(radian_formula, self.antialias)
        return warp(img)


class RadianSqrtEffect(RadianFormulaEffect):
    name = 'r = sqrt(r)' 
    def __init__(self):
        super(RadianSqrtEffect, self).__init__(
            lambda r, phi: (math.sqrt(r), phi))
        

class WaveEffect(Effect):
    name = 'Wave Effect'
    def __init__(self, vertical_delta=0.1, horizon_delta=0, box=None):
        self.vertical_delta = vertical_delta
        self.horizon_delta = horizon_delta
        self.box = box

    def filter(self, img):
        if self.box == None:
            left, top = 0, 0
            right, bottom = img.size[0] - 1, img.size[1] - 1
        else:
            left, top, right, bottom = self.box

        width, height = img.size

        mid_x = (right + left) / 2.0
        mid_y = (top + bottom) / 2.0 

        new_img = img.copy()
        height_delta = (bottom - top + 1) * self.vertical_delta 
        width_delta = 2 * math.pi / (right - left + 1) * (self.horizon_delta + 1)
        for x in range(left, right):
            degree = x * width_delta
            for y in range(top, bottom):
                h = math.sin(degree) * height_delta * ((bottom - top) / 2 - math.sqrt((y - mid_y) ** 2 + (x - mid_x) ** 2)) / mid_y
                offset = int(round(h))
                if 0 < x < width and 0 < y + offset < height:
                    new_img.putpixel((x, y), img.getpixel((x, y + offset)))
                else:
                    new_img.putpixel((x, y), Effect.empty_color)

        return new_img


class EffectGlue(Effect):
    name = 'Effect Glue'
    def __init__(self, name=None):
        self.name = name if name else EffectGlue.name 
        self.effect_pipeline = []

    def append(self, effect):
        self.effect_pipeline.append(effect)

    def remove(self, effect):
        self.effect_pipeline.remove(effect)

    def insert(self, index, effect):
        self.effect_pipeline.insert(index, Effect)

    def pop(self):
        return self.effect_pipeline.pop()

    def filter(self, img):
        for f in self.effect_pipeline:
            img = f.filter(img)
        return img
        

class GridMaker(Effect):
    name = 'Grid Maker'
    def __init__(self, width_offset, height_offset, color=(0, 0, 0, 255)):
        self.width_offset = width_offset
        self.height_offset = height_offset
        self.color = color

    def filter(self, img):
        width, height = img.size

        # draw grid
        draw = ImageDraw.Draw(img) 
        for x in range(0, width, self.width_offset):
            draw.line((x, 0, x, height), self.color) 
        for y in range(0, height, self.height_offset):
            draw.line((0, y, width, y), self.color) 

        del draw
        return img


class TextWriter(Effect):
    name = 'Text Writer'
    def __init__(self, (x, y), text, color=(0, 0, 0, 255), font=None):
        self.x = x
        self.y = y
        self.text = text
        self.color = color

    def filter(self, img):
        draw = ImageDraw.Draw(img) 
        draw.text((self.x, self.y), self.text, self.color)
        del draw
        return img
        

def GenerateImage(effect):
    # draw img
    # img = Image.open('z.jpg')
    img = Image.new("RGBA", (300, 300), (255, 255, 255, 255))

    width, height = img.size

    grid = GridMaker(20, 20)
    text = TextWriter((10, 100), string.letters)

    img = grid.filter(text.filter(img))

    old = img.copy()

    img = effect(img) 

    out = Image.new("RGBA", (width * 2, height))
    out.paste(old, (0, 0))
    out.paste(img, (width, 0)) 
    draw = ImageDraw.Draw(out) 

    draw.line((width, 0, width, height), (255, 0, 0, 255))

    out.save('haha.png')

def sign(v):
    return 1 if v >= 0 else -1
    
if __name__ == '__main__':
    wave = WaveEffect(0.2, 0.5, (100, 50, 200, 200))
    sqrt = RadianSqrtEffect()
    effect = RadianFormulaEffect(lambda r, phi: (r ** 1.2, phi))
    effect = RadianFormulaEffect(lambda r, phi: (r ** 1.5 * math.cos(r), phi))
    effect = RadianFormulaEffect(lambda r, phi: (r, phi + 0.5))
    effect = GlobalWarpEffect(lambda x, y: (x + 0.1, y))
    effect = GlobalWarpEffect(lambda x, y: (math.sin(x * math.pi / 2), math.sin(y * math.pi / 2)))
    effect = GlobalWarpEffect(lambda x, y: (sign(x) * x ** 2, sign(y) * y ** 2))
    effect = RadianFormulaEffect(lambda r, phi: (r ** 2, phi), 4)
    GenerateImage(effect)
