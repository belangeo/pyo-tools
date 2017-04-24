#!/usr/bin/env python

# Copyright 2017 Olivier Belanger
#
# This file is part of pyo-tools.
#
# pyo-tools is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyo-tools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with pyo-tools. If not, see <http://www.gnu.org/licenses/>.

# pyo-tools package setup script.

from distutils.core import setup

DESC = 'Repository of python classes for building audio fxs and synths with pyo.'

setup(name='pyotools',
      version='0.1.0',
      description=DESC,
      author='Olivier Belanger',
      author_email='belangeo@gmail.com',
      url='https://github.com/belangeo/pyo-tools/',
      packages=['pyotools'],
)
