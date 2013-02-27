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

from operator import attrgetter

from nose.tools import assert_equals
from nose.tools import assert_true
from nose.tools import assert_is
from nose.tools import assert_in
from nose.tools import assert_raises
from nose.tools import assert_raises_regexp

import requests

import rmock
from testtools import http_call

from rmock import call
from rmock.errors import InvalidFunction
from rmock.tools import find_random_port

class TestRmockFreeze(object):
    
    def test_freeze_call_simple(self):
        
        with rmock.run(port=find_random_port()) as mock:
            mock.func.return_value = 123
            mock.func2(a='10').return_value = 255
            
            mock.freeze_mock()
            
            assert_equals(http_call(mock, 'func').text,
                          '123')
            
            assert_equals(http_call(mock, 'func5').code,
                          404)
            
            assert_raises(InvalidFunction,
                          attrgetter('func3.return_value'),
                          mock)
