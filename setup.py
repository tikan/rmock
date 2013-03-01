#!/usr/bin/env python

#
# Copyright 2013 Dreamlab Onet.pl
# 
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation;
# version 3.0.
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, visit
#
# http://www.gnu.org/licenses/lgpl.txt
#

from setuptools import setup
from setuptools import find_packages

def read_file(filename):
    with open(filename) as f:
        return f.read()

setup(
    name='rmock',
    version='0.3.2',
    description='remote mocks library',
    url='http://doc.grupa.onet/display/Poczta',    
    author='Krzysztof Chmiel',
    author_email='krzysztof.chmiel@grupaonet.pl',    
    package_dir = {'':'src'}, 
    packages=find_packages('src'),
    long_description=read_file('README.rst'),
    install_requires=[
        'tornado>=2.0',
        'phpserialize>=1.2',
        'python-memcached>=1.48'
    ]
)
