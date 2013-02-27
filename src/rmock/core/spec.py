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

class Spec(object):
    
    def __init__(self):
        self.mod_callbacks = []
    
    def apply(self, rmock):
        pass
    
    def set_modified(self):
        for callback in self.mod_callbacks:
            callback()
    
    def add_modified_callback(self, callback):
        self.mod_callbacks.append(callback)
    
    def reset(self):
        pass
