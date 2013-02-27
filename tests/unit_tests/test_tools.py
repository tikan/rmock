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
from nose.tools import assert_true
from nose.tools import assert_false

from rmock.tools import dict_apply
from rmock.tools import dict_contains

from rmock.tools import len_trim

class TestTools(object):
    
    def test_len_trim(self):
        assert_equals(len_trim(100*'a', 10), 7 * 'a' + '...')
        assert_equals(len_trim(100 * 'a', 10), 7 * 'a' + '...')
        assert_equals(len_trim('', 10), '')
        assert_equals(len_trim('abc', 3), 'abc')
    
    def test_dict_apply(self):
        dct = {'a': [1, 2, 3, 4],
               'b': {'c': [1, 3],
                     'e': 1000 * 'a'}}
        
        dct_mod = dict_apply(dct, lambda x: x * 3)
        assert_equals(dct, {'a': [1, 2, 3, 4],
                            'b': {'c': [1, 3],
                                  'e': 1000 * 'a'}})
        
        assert_equals(dct_mod, {'a': [3, 6, 9, 12],
                            'b': {'c': [3, 9],
                                  'e': 3000 * 'a'}})
    
    def test_dict_apply_with_tuples(self):
        dct = (3, {'a': (1, 2, 3, 4),
                   'b': ('a', 'b', 'c')})
        
        dct_mod = dict_apply(dct, lambda x: x * 3)
        assert_equals(dct,  (3, {'a': (1, 2, 3, 4),
                                       'b': ('a', 'b', 'c')}))
        
        assert_equals(dct_mod, 
                      (9, {'a': (3, 6, 9, 12),
                           'b': (3 * 'a', 3 * 'b', 3 * 'c')}))
    
    def test_len_trim_dict(self):
        dct = {'a': [1, 2, 3, 4],
               'b': {'c': [1, 3],
                     'e': 1000 * 'a'}}
        
        dct_mod = dict_apply(dct, lambda x: len_trim(x, 100) if isinstance(x, basestring) else x)
        assert_equals(dct, {'a': [1, 2, 3, 4],
                            'b': {'c': [1, 3],
                                  'e': 1000 * 'a'}})
        
        assert_equals(dct_mod, {'a': [1, 2, 3, 4],
                            'b': {'c': [1, 3],
                                  'e': 97 * 'a' + '...'}})
    
    def test_dict_contains(self):
        assert_true(dict_contains({}, {}))
        assert_true(dict_contains({'a': 10}, {'a': 10}))
        assert_true(dict_contains({'a': 10}, {'a': 10, 'b': 20}))
        
        assert_false(dict_contains({'a': 10, 'b': 20}, {}))
        
        assert_false(dict_contains({'a': 10}, {'a': 11, 'b': 20}))
        assert_false(dict_contains({'a': 10}, {'a': 11, 'b': None}))
