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
from nose.tools import assert_raises

from memcache import Client

import requests

import rmock 
from rmock.comparators import any_

from rmock import params_subset
from rmock import call

from testtools import http_call
from testtools import memcache_call

class TestCallSubset(object):
    
    def test_call_subset_simple(self):
        
        with rmock.patch("http", port="random") as mock:
            
            mock.parse.return_value = 'standardresult'
            
            mock.parse(params_subset(a='10')).return_value = 'aresult'
            
            assert_equals(http_call(mock, 'parse', a=10, b=20).text,
                          'aresult')
            
            assert_equals(http_call(mock, 'parse', a=10).text,
                          'aresult')
            
            assert_equals(http_call(mock, 'parse', b=10).text,
                          'standardresult')
            
            assert_equals(http_call(mock, 'parse').text,
                          'standardresult')
    
    def test_call_subset_assert_simple(self):
        
        with rmock.patch("memcache", port="random") as mock:
            
            memcache_call(mock, 'set', "a", "b", time=20)
            
            mock.set.assert_called_with("a", "b", time=20)
            mock.set.assert_called_with("a", "b", time=any_())
            mock.set.assert_called_with(params_subset("a", "b"))
        
        with rmock.patch("http", port="random") as mock:
            http_call(mock, 'parse', a=10, b=20)
            
            mock.assert_called_with(params_subset())
            mock.assert_called_with(params_subset(a='10'))
            mock.assert_called_with(params_subset(a='10', b='20'))
            mock.assert_not_called_with(params_subset(a='10', b='20', c='30'))
            mock.assert_not_called_with(params_subset(a=10))
    
    def test_call_subset_with_call(self):
        
        with rmock.run() as mock:

            http_call(mock, 'parse', a='10', b='20')
            http_call(mock, 'parse', a='10', b='20', c='30')
            http_call(mock, 'parse', param1='value1', param2='value2')
            http_call(mock, 'parse')
            
            mock.parse.assert_has_calls([
                call(params_subset()),
                call(params_subset(a='10')),
                call(params_subset(a='10', b='20')),
                call(params_subset(param1='value1')),
            ], check_call_count=False)
            
            assert_raises(AssertionError,
                mock.parse.assert_has_calls,
                [call(params_subset(e=10)),
            ], check_call_count=False)
        
