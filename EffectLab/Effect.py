#!/usr/bin/env python
# -*- coding: utf-8 -*-  
# author:  Hua Liang [ Stupid ET ]
# email:   et@everet.org
# website: http://EverET.org
#

# Rule Of Optimization: Prototype before polishing. Get it
#                       working before you optimize it.

import random, string, md5, time
import Image, ImageDraw, ImageFont, ImageChops, ImageFilter
import StringIO
import math, operator
from math import sqrt, sin, cos, atan2

# Effect是特效处理流程中的过滤器，输入PIL中的Image，然后输出处理好的Image
# 其中，（）是经过重载的，默认调用成员函数filter(img)。这样可以方便的与其他普通过滤器函数组合在一起。
#

class Effect(object):
    '''The base Effect
    '''
    name = 'Base Effect'
    empty_color = (128, 128, 128, 255)
    def __init__(self):
        pass

    def __call__(self, img):
        '''重载（），模仿C++中的仿函数。
        '''
        return self.filter(img)

    def filter(self, img):
        return img


class RegionWarpEffect(Effect):
    def __init__(self, formula, antialias=2, box=None):
        self.formula = formula
        self.antialias = antialias
        self.box = box

    def filter(self, img):
        width, height = img.size
        new_img = Image.new(img.mode, img.size, Effect.empty_color)

        nband = len(img.getpixel((0, 0)))
        antialias = self.antialias
        left, top, right, bottom = self.box if self.box else (0, 0, width, height)
            
        for x in xrange(left, right):
            for y in xrange(top, bottom): 
                found = 0
                psum = (0, ) * nband

                # anti-alias
                for ai in xrange(antialias):
                    _x = x + ai / float(antialias)
                    for aj in xrange(antialias):
                        _y = y + aj / float(antialias)

                        u, v = self.formula(_x, _y)

                        u = int(round(u))
                        v = int(round(v))
                        if not (0 <= u < width and 0 <= v < height):
                            continue
                        pt = img.getpixel((u, v))
                        psum = map(operator.add, psum, pt)
                        found += 1 

                if found > 0:
                    psum = map(operator.div, psum, (found, ) * len(psum)) 
                    new_img.putpixel((x, y), tuple(psum))

        return new_img 
        
        
class LocalWarpEffect(Effect):
    '''Interactive Image Warping Effect
    @note 参考文献: Interactive Image Warping by Andreas Gustafsson 
    '''
    def __init__(self, center, mouse, radius, antialias=2):
        '''
        @param center 局部变形效果的圆心，可以认为是鼠标按下起点
        @param mouse 鼠标释放的位置
        '''

        self.center = center
        self.mouse = mouse
        self.radius = radius
        self.antialias = antialias

    def warp(self, x, y, r, center, mouse):
        cx, cy = center
        mx, my = mouse
        dis_x_c = sqrt((x - cx) ** 2 + (y - cy) ** 2) 
        dis_m_c = sqrt((x - mx) ** 2 + (y - my) ** 2) 
        div = float(r ** 2 - dis_x_c ** 2 + dis_m_c ** 2) 
        if div == 0:
            div = 0.0000000001
        factor = ((r ** 2 - dis_x_c ** 2) / div) ** 2

        u = x - factor * (mx - cx)
        v = y - factor * (my - cy) 

        return u, v

    def filter(self, img):
        width, height = img.size
        new_img = img.copy()
        r = self.radius
        cx, cy = self.center
        mx, my = self.mouse

        nband = len(img.getpixel((0, 0)))
        antialias = self.antialias
        for x in xrange(width):
            for y in xrange(height):
                if sqrt((x - cx) ** 2 + (y - cy) ** 2) > r:
                    continue

                found = 0
                psum = (0, ) * nband

                # anti-alias
                for ai in xrange(antialias):
                    _x = x + ai / float(antialias)
                    for aj in xrange(antialias):
                        _y = y + aj / float(antialias)

                        u, v = self.warp(_x, _y, r, (cx, cy), (mx, my))
                        u = int(round(u))
                        v = int(round(v))
                        if not (0 <= u < width and 0 <= v < height):
                            continue
                        pt = img.getpixel((u, v))
                        psum = map(operator.add, psum, pt)
                        found += 1 

                if found > 0:
                    psum = map(operator.div, psum, (found, ) * len(psum)) 
                    new_img.putpixel((x, y), tuple(psum))

        return new_img 


class LensWarpEffect(Effect):
    '''Lens warping Effect
    全局性的镜头变形效果，构造的时候需要输入一个变换方程
    f(x, y) => (x', y').其中，x和y都被规范化为-1到1的取值。
    参考资料：http://paulbourke.net/miscellaneous/imagewarp/
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
        for j in xrange(height):
            for i in xrange(width):
                found = 0
                psum = (0, ) * nband
                new_img.putpixel((i, j), Effect.empty_color)
                # antialias
                for ai in xrange(self.antialias):
                    x = 2 * (i + ai / float(self.antialias)) / width - 1
                    for aj in xrange(self.antialias):
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
                    psum = map(operator.div, psum, (found, ) * len(psum)) 
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
            r = sqrt(x ** 2 + y ** 2)
            phi = atan2(y, x)

            r, phi = self.formula(r, phi)

            xnew = r * cos(phi)
            ynew = r * sin(phi)

            return xnew, ynew

        warp = LensWarpEffect(radian_formula, self.antialias)
        return warp(img)


class RadianSqrtEffect(RadianFormulaEffect):
    name = 'r = sqrt(r)' 
    def __init__(self):
        super(RadianSqrtEffect, self).__init__(
            lambda r, phi: (sqrt(r), phi))
        
class GlobalWaveEffect(Effect):
    '''全局波浪效果，使用sin进行变换
    '''
    def __init__(self, dw=1, dh=0.1, antialias=2):
        self.dw = dw
        self.dh = dh
        self.antialias = antialias

    def transform(self, x, y, width, height, delta_w, delta_h):
        radian = 2 * math.pi * x / float(width) * delta_w
        offset = 0.5 * sin(radian) * height * delta_h

        return x, y + offset
        
    def filter(self, img):
        width, height = img.size
        f = lambda x, y: self.transform(x, y, width, height, self.dw, self.dh)
        warp = RegionWarpEffect(f, self.antialias)
        return warp(img)

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
        for x in xrange(left, right):
            degree = x * width_delta
            for y in xrange(top, bottom):

                # distortion
                h = sin(degree) * height_delta * ((bottom - top) / 2 - sqrt((y - mid_y) ** 2 + (x - mid_x) ** 2)) / mid_y
                offset = int(round(h))
                _x = x
                _y = y + offset

                if 0 < x < width and 0 < _y < height:
                    new_img.putpixel((x, y), img.getpixel((x, _y)))
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
    '''用于绘制网格'''
    name = 'Grid Maker'
    def __init__(self, width_offset, height_offset, color=(0, 0, 0, 255)):
        self.width_offset = width_offset
        self.height_offset = height_offset
        self.color = color

    def filter(self, img):
        width, height = img.size

        # draw grid
        draw = ImageDraw.Draw(img) 
        for x in xrange(0, width, self.width_offset):
            draw.line((x, 0, x, height), self.color) 
        for y in xrange(0, height, self.height_offset):
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
        if font:
            raise NotEmplementedError
        self.font = font

    def filter(self, img):
        draw = ImageDraw.Draw(img) 
        draw.text((self.x, self.y), self.text, self.color)
        del draw
        return img
        
def sign(v):
    return 1 if v >= 0 else -1
    
