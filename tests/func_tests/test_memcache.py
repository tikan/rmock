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

import time
import memcache

import rmock

from rmock.errors import RmockParamsError
from rmock.tools import find_random_port 

from rmock import call
from rmock import params_subset

from rmock.runners.memcache.spec import MemcacheSpec

from nose.tools import assert_raises
from nose.tools import assert_equals
from nose.tools import assert_true

class TestMemcache(object):
    
    @classmethod
    def setup_class(cls):
        port = find_random_port()
        cls.mock = rmock.run('memcache', port=port)
        cls.client = memcache.Client(['localhost:%s' % port])

    def setup(self):
        self.mock.reset_mock()
    
    def teardown(self):
        self.mock.reset_mock()

    def test_memcache_get_set(self):
        
        self.mock.get('aaa').return_value = 'zzz'        
        
        assert_equals(self.client.get('aaa'), 'zzz')
        assert_equals(self.client.set('aaa', 'bbb'), 1)  
        assert_equals(self.client.delete('aaa'), 1)
        
        self.mock.set.assert_called_with('aaa', 'bbb', time=0)        
        self.mock.get.assert_called_with('aaa')
        self.mock.delete.assert_called_with('aaa')
        
    def test_memcache_set_fail(self):
        self.mock.set.return_value = 0
        set_result = self.client.set('xyzx', '123', time=123)
        assert_equals(set_result, 0)
        
        self.mock.set.assert_called_with('xyzx', '123', time=123)
        
    def test_memcache_delete_fail(self):
        self.mock.delete.return_value = 0
        delete_result = self.client.delete('zzz')
        
        # python client do not verify delete result
        #assert_equals(delete_result, 0)
        
        self.mock.delete.assert_called_with('zzz',)
    
    def test_memcache_with_quit(self):
        self.mock.delete.return_value = 0
        set_result = self.client.set('zzz', 'xxx')
        assert_equals(set_result, 1)
        self.client.disconnect_all()
        
        self.mock.set.assert_called_with('zzz', 'xxx', time=0)
    
    def test_memcache_url_param(self):
        
        with rmock.run('memcache', url='localhost:10005') as memcache_mock:
            client = memcache.Client(['localhost:10005'])
            
            client.get("10")
            memcache_mock.get.assert_called_with("10")
    
    def test_memcache_url_param_error(self):
        
        assert_raises(
            RmockParamsError,
            rmock.run,
            "memcache",
            url='localhost:zzz'
        )
        
        assert_raises(
            RmockParamsError,
            rmock.run,
            "memcache",
            url='localhost:333,127.0.0.1:222'
        )            
        
        assert_raises(
            RmockParamsError,
            rmock.run,
            "memcache",
            port=4455,
            url='localhost:11211'
        )
        
        assert_raises(
            RmockParamsError,
            rmock.run,
            "memcache",
            url='localhost:333,127.0.0.1:222'
        )
    
    def test_memcache_two_clients(self):
        
        spec = MemcacheSpec()
                
        with rmock.run("memcache", port="random", spec=spec) as memcache_mock:
            
            client1 = memcache.Client(['localhost:%s' % memcache_mock.runner_params.port])
            
            client1.get('a')
            
            client2 = memcache.Client(['localhost:%s' % memcache_mock.runner_params.port])            
            
            set_result = client2.set('a', 'b')
            assert_true(set_result)
            
            client2.get('b')
            client1.get('c')
            
            set_result = client1.set('b', 'a')
            assert_true(set_result)
            
            set_result = client1.set('c', 'e', time=444)
            assert_true(set_result)
            
            set_result = client2.set_multi(dict(d='e',
                                                e='f'),
                                           time=12)
            
            assert_equals(client1.get('e'), 'f')  
            assert_equals(client2.get('d'), 'e')
            
            memcache_mock.set.assert_has_calls([call('a', 'b', time=0),
                                                call('b', 'a', time=0),
                                                call('c', 'e', time=444),
                                                call('d', 'e', time=12),
                                                call('e', 'f', time=12)])
            
            memcache_mock.get.assert_has_calls([call('a'),
                                                call('b'),
                                                call('c'),
                                                call('d'),
                                                call('e')])

class TestMemcacheSpec(object):
    
    def test_memcache_spec_basic(self):
        
        spec = MemcacheSpec()
        
        with rmock.run("memcache",
                       port=find_random_port(),
                       spec=spec) as mock:
            
            client = memcache.Client(['localhost:{port}'.format(**mock.runner_params)])
            
            assert_equals(client.get('a'), None)
            client.set('a', '10')
            assert_equals(client.get('a'), '10')
            
            client.delete('a')
            assert_equals(client.get('a'), None)
            mock.get.assert_has_calls([call('a'), call('a'), call('a')])
            mock.set.assert_called_once_with(params_subset('a', '10'))
            mock.delete.assert_called_once_with('a')
    
    def test_memcache_spec_add_value(self):
        
        spec = MemcacheSpec({'key': 'value'})
        
        with rmock.run("memcache",
                       port=find_random_port(),
                       spec=spec) as mock:
            
            client = memcache.Client(['localhost:{port}'.format(**mock.runner_params)])
            assert_equals(client.get('key'), 'value')
            
            assert_equals(client.get('key2'), None)
            spec.add_value('key2', 'value2')
            assert_equals(client.get('key2'), 'value2')
