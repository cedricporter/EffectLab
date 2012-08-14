#!/usr/bin/env python
# -*- coding: utf-8 -*-  
# author:  Hua Liang [ Stupid ET ]
# email:   et@everet.org
# website: http://EverET.org
#

import os 
from EffectLab.Effect import *

Effect.empty_color = (255, 255, 255, 255)

if __name__ == '__main__':
    from timeit import Timer
    from functools import partial
    import cProfile

    img = Image.new("RGB", (100, 100))
    wave = GlobalWaveEffect(1, 0.5)
    test = partial(wave, img)

    profile = False
    if profile:
        cProfile.run("test()", "profile.data")

        import pstats
        #创建Stats对象
        p = pstats.Stats("profile.data")
        # p.strip_dirs().sort_stats(-1).print_stats()
        # p.strip_dirs().sort_stats("cumulative").print_stats()
        p.strip_dirs().sort_stats("time").print_stats()
    else: 
        t = Timer('test()', 'from __main__ import test') 
        N = 3
        TIMES = 30
        print sum(t.repeat(N, TIMES)) / N / TIMES * 1000, 'ms'

