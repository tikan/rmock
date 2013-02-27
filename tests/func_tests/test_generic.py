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

import logging
from urllib2 import urlopen
from urllib2 import URLError
import time
import socket

import requests

from nose.tools import assert_equals
from nose.tools import assert_true
from nose.tools import assert_is
from nose.tools import assert_in
from nose.tools import assert_raises
from nose.tools import assert_raises_regexp

import rmock
from rmock.errors import RmockError
from rmock.tools.net import find_random_port

from nose.plugins.skip import SkipTest

from testtools import http_call

class TestRmockGeneric(object):
    
    def test_rmock_run_with_key(self):
        mock = rmock.run(key="myrmock",
                         port="random")
        
        assert_is(mock, rmock.get("myrmock"))
    
    def test_server_already_running(self):
        
        port = find_random_port()
        with rmock.run(port=port):
        
            assert_raises_regexp(
                RmockError,
                'error starting server process.*port.*%s.*' % port,
                rmock.run,
                port=port
            )
    
    @rmock.patch(port="random")
    def test_stop_server(self, mock):
        
        assert_equals(http_call(mock, "func").text, '')
        mock.stop_server()
        
        assert_raises(requests.ConnectionError,
                      http_call,
                      mock,
                      'func')
        
        mock.start_server()
        assert_equals(http_call(mock, 'func').text, '')
    
    def _func_side_effect(self, arg):
        return arg
    
    def _func_side_effect2(self, a, b, c):
        return '.'.join([a, b, c])
    
    @rmock.patch(port="random")
    def test_function_side_effect(self, mock):
        
        mock.func.side_effect = self._func_side_effect
        mock.set_default_side_effect(self._func_side_effect2)        
        
        assert_equals(http_call(mock, 'func', arg="val").text, 'val')
        assert_equals(http_call(mock, 'func', arg="val2").text, 'val2')
        
        assert_equals(http_call(mock, 'defaultfunc', a=10, b=20, c=30).text, '10.20.30')
        
        assert_equals(len(mock.func.calls), 2)
        assert_equals(mock.func.calls[0].args, ())
        assert_equals(mock.func.calls[0].kwargs, {'arg': 'val'})
    
    def test_rmock_create(self):
        mock = rmock.create("http", port="random")
        mock.func.return_value = "result"
        
        assert_raises(requests.ConnectionError, http_call, mock, "func")
        
        mock.start_server()
        assert_equals(http_call(mock, "func").text, "result")
        assert_equals(http_call(mock, "func2").text, "")
        
        mock.func.return_value = "other result"
        assert_equals(http_call(mock, "func").text, "other result")
        
        mock.start_server()
        assert_equals(http_call(mock, "func").text, "other result")

@SkipTest
#("mock.patch only support class functions now")
@rmock.patch("http", port="random")
def test_free_func(mock):
        
    http_call(mock, "func")
    mock.assert_called_with()
