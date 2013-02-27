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

import logging

import requests

import rmock
from rmock import call

from rmock.runners.http.proxy.choosers import HeaderBasedChooser
from testtools import http_call

from nose.tools import assert_equals

class TestHttpProxy(object):
    
    def test_http_proxy_simple(self):
        first = rmock.run(port="random", key="first")
        second = rmock.run(port="random", key="second")
        
        first.func.return_value = "first"
        second.func.return_value = "second"
        
        proxy = rmock.run("http-proxy",
                          [first, second],
                          child_chooser=HeaderBasedChooser('Choose'),
                          port="random")
        
        assert_equals(http_call(proxy, 'func', headers={'choose': 'first'}, a=10).text,
                      'first')
        assert_equals(http_call(proxy, 'func', headers={'choose': 'first'}, b=10).text,
                      'first')
        assert_equals(http_call(proxy, 'func', headers={'choose': 'second'}, c=10).text,
                      'second')
        assert_equals(http_call(proxy, 'func', headers={'choose': 'unknown'}, a=10).code,
                      404)
        
        first.func.assert_has_calls([call(a='10'), call(b='10')])
        second.func.assert_has_calls([call(c='10')])
