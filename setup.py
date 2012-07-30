#!/usr/bin/env python
# -*- coding: utf-8 -*-  
# author:  Hua Liang [ Stupid ET ]
# email:   et@everet.org
# website: http://EverET.org
#

from distutils.core import setup, Extension
import re

NAME = "EffectLab"
DESCRIPTION = "Python Image Processing Effect Lab"
AUTHOR = "Hua Liang [Stupid ET]"
HOMEPAGE = "http://everet.org/2012/07/effectlab.html"
DOWNLOAD_URL = "https://github.com/cedricporter/EffectLab/downloads"

def find_version(filename):
    for line in open(filename).readlines():
        m = re.search("VERSION\s*=\s*\"([^\"]+)\"", line)
        if m:
            return m.group(1)
    return None

VERSION = find_version("EffectLab/Effect.py")

setup(name = NAME,
      version = VERSION,
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
