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

import _pythonpath

from nose.tools import assert_equals
from nose.tools import assert_not_equals
from nose.tools import assert_true

from rmock.comparators import any_
from rmock.comparators import none_
from rmock.comparators import is_
from rmock.comparators import contains
from rmock.comparators import re_matches
from rmock.comparators import func_eq
from rmock.comparators import greater
from rmock.comparators import greater_eq
from rmock.comparators import less
from rmock.comparators import less_eq
from rmock.comparators import between
from rmock.comparators import between_eq
from rmock.comparators import any_of

class TestComparators(object):
    
    def test_any(self):
        assert_equals(10, any_())
        assert_equals(None, any_())
        assert_equals('123', any_())
    
    def test_none(self):
        assert_not_equals(10, none_())
        assert_not_equals(None, none_())
        assert_not_equals('123', none_())
    
    def test_is(self):
        assert_equals(10, is_(int))
        assert_not_equals('10', is_(int))
        assert_equals('10', is_(str))
        assert_equals(None, is_(type(None)))        
        assert_not_equals('10', is_(type(None)))
    
    def test_str_contains(self):
        assert_equals('123', contains('1'))
        assert_not_equals('123', contains('4'))
    
    def test_re_matches(self):
        
        assert_equals('123', re_matches(r'\d+'))
        assert_equals('21321', re_matches(r'.*'))
        assert_not_equals(21321, re_matches(r'.*'))

    def test_func(self):
        
        func1 = func_eq(lambda value: value >= 120)        
        assert_equals(123, func1)
        assert_not_equals(119, func1)
        
        assert_true(str(func1))
    
    def test_greater(self):
        assert_equals(1, greater(0))
        assert_not_equals(-1, greater(0))
        assert_not_equals(0, greater(0))
    
    def test_greater_eq(self):
        assert_equals(1, greater_eq(0))
        assert_not_equals(-1, greater_eq(0))
        assert_equals(0, greater_eq(0))
    
    def test_less(self):
        assert_not_equals(1, less(0))
        assert_equals(-1, less(0))
        assert_not_equals(0, less(0))
    
    def test_less_eq(self):
        assert_not_equals(1, less_eq(0))
        assert_equals(-1, less_eq(0))
        assert_equals(0, less_eq(0))
    
    def test_between(self):
        assert_equals(1, between(0, 2))
        assert_not_equals(1, between(3, 4))
        assert_not_equals(1, between(1, 2))
        assert_not_equals(2, between(1, 2))
    
    def test_between_eq(self):
        assert_equals(1, between_eq(0, 2))
        assert_not_equals(1, between_eq(3, 4))
        assert_equals(1, between_eq(1, 2))
        assert_equals(2, between_eq(1, 2))
    
    def test_any_of(self):
        assert_equals(1, any_of((1, 2)))
        assert_equals('any', any_of(('any')))
        assert_equals('', any_of(['', None, 1]))
        assert_not_equals('', any_of([]))
        assert_not_equals('x', any_of(['y', 'z']))
        