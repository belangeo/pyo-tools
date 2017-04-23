#!/usr/bin/env python
#------------------------------------------
# pyodev package setup script.
#
# Author: Olivier Belanger, (c) LGPL, 2017.
#------------------------------------------

from distutils.core import setup

DESC = 'Repository of python classes for building audio fxs and synths with pyo.'

setup(name='pyodev',
      version='0.1.0',
      description=DESC,
      author='Olivier Belanger',
      author_email='belangeo@gmail.com',
      url='https://github.com/belangeo/pyo-dev/',
      packages=['pyodev'],
)
