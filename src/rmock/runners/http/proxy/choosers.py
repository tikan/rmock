# coding=utf8

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

import random

def random_chooser(request_data, mocks):
    return random.choice(mocks)

class HeaderBasedChooser(object):
    
    def __init__(self, header_name):
        self.header_name = header_name
    
    def __call__(self, call, mocks):
        headers = call.headers
        header_value = headers.get(self.header_name, '')
        
        return next((mock for mock in mocks if mock.name == header_value), None)
