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

import time

import requests
import memcache

import rmock
from rmock import timeout_side_effect
from rmock.tools import RANDOM_PORT

from nose.tools import assert_equals
from nose.tools import assert_raises
from nose.tools import assert_true

from testtools import http_call, memcache_call

class TestRmockTimeouts(object):
        
    def test_rmock_timeoutes_http(self):
        
        with rmock.patch("http", port=RANDOM_PORT) as mock:
            
            mock.parse.side_effect = timeout_side_effect(.5)
            
            assert_raises(
                requests.Timeout,
                http_call,
                mock,
                'parse',
                a=10,
                b=20,
                timeout=0.2
            )
    
    def test_rmock_timeoutes_memcache(self):
        
        with rmock.patch("memcache", port=RANDOM_PORT) as mock:
            
            cli = memcache.Client(['localhost:{port}'.format(**mock.runner_params)])
            
            mock.get.return_value = 'isok'
            
            assert_equals(memcache_call(mock, 'get', 'testkey', timeout=0.2),
                          'isok')
            
            mock.get.side_effect = timeout_side_effect(0.4, 'isok')
            assert_equals(memcache_call(mock, 'get', 'testkey', timeout=0.2), None)
            
            # wait for previous request to finish
            time.sleep(0.4)
            
            mock.get.side_effect = timeout_side_effect(0.1, 'isok')
            assert_equals(memcache_call(mock, 'get', 'testkey23333', timeout=0.2),
                          'isok')
