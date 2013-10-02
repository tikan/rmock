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
#TODO: refactoring

class Call(object):
    
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.funcname = None
        self.headers = None
    
    def __getitem__(self, index):
        """Allow tuple-like access"""
        return (self.args, self.kwargs)[index]
    
    @staticmethod
    def _make(funcname, args, kwargs, headers=None):
        result = Call(*args, **kwargs)
        result.funcname = funcname
        result.headers = headers
        
        return result
    
    def _to_tuple(self, ext=False):
        if ext:
            return (self.funcname, self.args, self.kwargs)
        
        return (self.args, self.kwargs)
    
    def __eq__(self, value):
        if isinstance(value, Call):
            return self._to_tuple(ext=True) == self._to_tuple(ext=True)
        
        try:
            ext = (len(value) == 3)
        except TypeError:
            return False
        
        return self._to_tuple(ext=ext) == value
    
    def __str__(self):
        if self.funcname is not None:
            pattern = "call(funcname={funcname} args={args} kwargs={kwargs})"
        else:
            pattern = "call(args={args} kwargs={kwargs})"
        
        return pattern.format(**self.__dict__)
    
    __repr__ = __str__
    
