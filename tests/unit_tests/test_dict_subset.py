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

from nose.tools import assert_equals
from nose.tools import assert_not_equals

from rmock.core.function import DictSubset

def test_dict_subset_equal():
    assert_equals(DictSubset(), {}) 
    assert_equals({}, DictSubset())
    assert_equals(DictSubset(), DictSubset())
    assert_equals(dict(a=10, b=20, c=30), DictSubset(a=10))
    assert_equals(dict(a=10, b=20, c=30), dict(a=10, b=20, c=30))    
    assert_equals(dict(a=10, b=20, c=30), DictSubset(b=20))
    assert_equals(DictSubset(b=20), dict(a=10, b=20, c=30))
    assert_equals(DictSubset(b='b'), DictSubset(b='b'))
    
    assert_equals(DictSubset(b='b'), {'b': 'b', 'c': 2})
    assert_equals(DictSubset(b='b'), DictSubset(b='b', c='c'))

def test_dict_subset_not_equal():
    assert_not_equals(DictSubset(b='b'), DictSubset(b='c'))
    assert_not_equals(dict(b=20), DictSubset(b='b'))
