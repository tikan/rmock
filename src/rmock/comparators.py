# coding=utf8

"""Set of tools intended to be used in mock assertions"""

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

import operator
import re

class any_(object):

    """Always match"""

    def __eq__(self, other):
        return True
    
    def __repr__(self):
        return '<anything>'

class none_(object):

    """Never match"""

    def __eq__(self, other):
        return False
    
    def __repr__(self):
        return '<nothing>'

class is_(object):

    """Match compatible types"""

    def __init__(self, type_):
        self.type_ = type_
    
    def __eq__(self, other):
        return isinstance(other, self.type_)    
    
    def __repr__(self):
        return "<type is '%s'>" % self.type_.__name__

class contains(object):

    """Match using string operator 'in'"""

    def __init__(self, str_):
        self.str_ = str_
    
    def __eq__(self, other):
        return isinstance(other, basestring) and self.str_ in other
    
    def __repr__(self):
        return "<string containing '%s'>" % self.str_

class re_matches(object):

    """Match using regular expression"""

    def __init__(self, regexp, flags=0):
        self.regexp = regexp
        self.flags = flags
    
    def __eq__(self, other):
        return isinstance(other, basestring) and re.match(self.regexp, other, flags=self.flags)
    
    def __repr__(self):
        return "<string matching '%s'>" % self.regexp

class func_eq(object):

    """Match using given function"""

    def __init__(self, callable_):
        self.callable_ = callable_
    
    def __eq__(self, other):
        return self.callable_(other)
    
    def __repr__(self):
        return "<callable '%s'>" % self.callable_

class _compare_base(object):
    
    compare_func = None
    
    def __init__(self, value):
        self.value = value
    
    def __eq__(self, other):
        return self.compare_func(other, self.value)
        
class greater(_compare_base):

    """Match using operator >"""

    compare_func = operator.gt
    
    def __repr__(self):
        return "<greater than %s>" % self.value

class greater_eq(_compare_base):

    """Match using operator >="""

    compare_func = operator.ge
    
    def __repr__(self):
        return "<greater (or equal) than %s>" % self.value

class less(_compare_base):

    """Match using operator <"""

    compare_func = operator.lt
    
    def __repr__(self):
        return "<less than %s>" % self.value

class less_eq(_compare_base):

    """Match using operator <="""

    compare_func = operator.le
    
    def __repr__(self):
        return "<less (or equal) than %s>" % self.value

class _between_base(object):
    
    def __init__(self, value1, value2):
        self.value1 = value1
        self.value2 = value2

class between(_between_base):

    """Match on range without bounds"""

    def __eq__(self, other):
        return self.value1 < other < self.value2
    
    def __repr__(self):
        return "<between %s and %s>" % (self.value1, self.value2)
    
class between_eq(_between_base):

    """Match on range with bounds"""

    def __eq__(self, other):
        return self.value1 <= other <= self.value2
    
    def __repr__(self):
        return "<between %s and %s>" % (self.value1, self.value2)

class any_of(object):

    """Match on at least one element of the given sequence"""

    def __init__(self, seq):
        self.seq = seq
    
    def __eq__(self, other):
        return other in self.seq
        
    def __repr__(self):
        return '<any_of %s>' % (self.seq,)
