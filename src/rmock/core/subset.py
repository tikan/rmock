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

from rmock.tools import dict_contains
from rmock.core.call import Call

class ParamsSubset(object):
    """
    Simple wrapper for (args, kwargs) tuple
    """
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        
    def __str__(self):
        return 'subset' + str((self.args, self.kwargs))
    
    __repr__ = __str__

class DictSubset(dict):
    """
    Dict subclass with redefined equality testing
    
    DictSubset (A) is equal to plain dict (B) if A is subset of B  
    @see: dict_contains
    Analogously, plain dict (A) is equal to DictSubset (B) if B is subset of A.
    Two DictSubset instances (A, B) are equal if A is subset of B and B is subset of A. 
     
    Note than in case of DictSubset instance and plain dict instance equality defined as above is not commutative.
    DictSubset could be used in definition of call results or in call asserts.

    """
    def __eq__(self, other):
        
        if not isinstance(other, dict):
            return dict.__eq__(self, other)
                
        is_other_subset = isinstance(other, DictSubset)
        
        if is_other_subset:
            return dict_contains(self, other) or dict_contains(other, self) 
        else:
            return dict_contains(self, other)

class CallSubset(Call):
    
    def __init__(self, *args, **kwargs):
        Call.__init__(self, ParamsSubset(*args, **kwargs))
