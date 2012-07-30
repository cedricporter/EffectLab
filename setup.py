#!/usr/bin/env python
# -*- coding: utf-8 -*-  
# author:  Hua Liang [ Stupid ET ]
# email:   et@everet.org
# website: http://EverET.org
#

from distutils.core import setup, Extension

NAME = "EffectLab"
DESCRIPTION = "Python Image Processing Effect Lab"
AUTHOR = "Hua Liang [Stupid ET]"
HOMEPAGE = "http://everet.org/2012/07/effectlab.html"
DOWNLOAD_URL = "https://github.com/cedricporter/EffectLab/zipball/master"

setup(name = NAME,
      version = '1.0',
      author = 'Hua Liang [Stupid ET]',
      author_email = 'et@everet.org',
      url = HOMEPAGE,
      download_url = DOWNLOAD_URL,
      description = DESCRIPTION,
      long_description = DESCRIPTION,
      packages = ['EffectLab'],
      license = "Python (MIT style)",
      platforms = "Python 1.5.2 and later and PIL 1.1.7 and later.",
      ext_modules = [Extension('EffectLab.EffectLabCore', ['EffectLab/core.c']),
                     ] 
      )
