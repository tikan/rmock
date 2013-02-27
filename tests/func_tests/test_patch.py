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

import memcache
from urllib2 import urlopen

from nose.tools import assert_equals
from nose.tools import assert_true
from nose.tools import assert_is

import rmock
from rmock.tools.net import find_random_port

from rmock.tools import RANDOM_PORT

from testtools import http_call, memcache_call, memcache_get, memcache_set

class TestRmockPatch(object):

    @rmock.patch(port=RANDOM_PORT,
                 slug='pref')
    def test_patch_simple(self, mock):
        http_call(mock, "func")
        mock.func.assert_called_with()
    
    @rmock.patch("memcache", port=RANDOM_PORT)
    @rmock.patch(port=RANDOM_PORT)
    def test_patch_stacked(self, http_mock, memcache_mock):
        
        http_call(http_mock, 'func')
        memcache_call(memcache_mock, 'get', '???')
                
        http_mock.func.assert_called_with()
        memcache_mock.get.assert_called_with('???')

@rmock.patch(port=RANDOM_PORT)
@rmock.patch(port=RANDOM_PORT)
class TestRmockPatchClass(object):
    
    def test_patch_class_1(self, mock1, mock2):
        self.utility()
        mock1.func.assert_not_called()
        
        http_call(mock2, 'func', a=10)
        http_call(mock1, 'func', b=20)
        
        mock2.func.assert_called_with(a='10')
        mock1.func.assert_called_with(b='20')
    
    def test_patch_class_2(self, mock1, mock2):
        mock1.func.assert_not_called()
        http_call(mock1, 'func')
        http_call(mock2, 'func')
        
        mock1.func.assert_called_with()
        mock2.func.assert_called_with()
        
        self.utility()
    
    #not patched
    def utility(self):
        pass

@rmock.patch(port=RANDOM_PORT,
             classvar='mymock')
class TestRmockPatchClassWithClassVar(object):
    
    def test_patch_class_1(self):
        
        assert_true(hasattr(self, 'mymock'))
        self.mymock.func.assert_not_called()
        
        http_call(self.mymock, 'func', a='10')
        
        self.mymock.func.assert_called_with(a='10')
    
    def test_patch_class_2(self):
        
        assert_true(hasattr(self, 'mymock'))
        self.mymock.func.assert_not_called()
        
        http_call(self.mymock, 'func')
        self.mymock.func.assert_called_with()
        self.mymock.func.assert_called_with()

class TestRmockPatchContextManager(object):
    
    def test_patch_context_manager(self):
        
        port = find_random_port()
        with rmock.patch("memcache", port=port) as memcache_mock:
            
            memcache_mock.get('a').return_value = 'b'
            #cli = memcache.Client(['localhost:36555'])
            get_result = memcache_get(memcache_mock, 'a')
            assert_equals(get_result, 'b')
            
            set_result = memcache_set(memcache_mock, 'a', 20)
            assert_equals(set_result, 1)
            
            memcache_mock.get.assert_called_with('a')
            memcache_mock.set.assert_called_with('a', '20', time=0)
        
        #server not running
        cli = memcache.Client(['localhost:' + str(port)])
        set_result = cli.set('a', 20)
        assert_equals(set_result, 0)
        
        with rmock.patch("memcache", port=port) as memcache_mock:
            cli = memcache.Client(['localhost:36555'])
            set_result = memcache_set(memcache_mock, 'a', 20)
            assert_equals(set_result, 1)

class Mparser(object):
    
    def __call__(self, **kwargs):
        return kwargs

class TestRmockPatchClassSideEffect(object):
    
    @rmock.patch(port=RANDOM_PORT)
    def test_patch_class_1(self, mparser_mock):

        mparser_mock.parse.side_effect = Mparser() 
        
        assert_equals(http_call(mparser_mock, 'parse', a=10).text,
                      "{'a': '10'}")
        
        mparser_mock.parse.assert_called_with(a='10')
