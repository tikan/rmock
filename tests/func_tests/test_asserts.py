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

import requests

from nose.tools import assert_equals
from nose.tools import assert_true
from nose.tools import assert_is
from nose.tools import assert_in
from nose.tools import assert_raises
from nose.tools import assert_raises_regexp

import rmock
from rmock import call
from rmock.tools import find_random_port

from testtools import http_call

PORT = find_random_port()

@rmock.patch("http",
             port=PORT,
             classvar="mock")
class TestRmockAsserts(object):
    
    def setup(self):
        self.port = PORT
    
    def test_assert_called_once_with(self):
        
        self.func_call('func1', a=10)
        self.func_call()
        self.func_call()
        
        self.mock.func1.assert_called_once_with(a='10')
        
        with assert_raises(AssertionError) as ctx:
            self.mock.func.assert_called_once_with()
        
        assert_in("func called 2 times (1 expected)", str(ctx.exception))
        
        with assert_raises(AssertionError) as ctx:
            self.mock.func.assert_called_once_with(a='aaa')
        
        assert_in("invalid func call", str(ctx.exception))
        
        with assert_raises(AssertionError) as ctx:
            self.mock.func22.assert_called_once_with()
        
        assert_in("not called at all", str(ctx.exception))

    def test_assert_called_not_called(self):
        self.func_call()
        
        with assert_raises(AssertionError) as ctx:
            self.mock.func.assert_not_called_with()
        
        assert_in("was unexpectedly called with desired arguments (1 times)", str(ctx.exception))

        with assert_raises(AssertionError) as ctx:
            self.mock.func.assert_not_called()
        
        assert_in("was unexpectedly called (1 times)", str(ctx.exception))

        self.mock.func123.assert_not_called_with()
 
    def test_default_return_value(self):
        assert_equals(self.func_call().text, '')
        self.mock.set_default_return_value(123)
        
        assert_equals(self.func_call().text, '123')
        self.mock.func.return_value = 321
        
        assert_equals(self.func_call().text, '321')
        assert_equals(self.func_call('func2').text, '123')
        
        self.mock.set_default_return_value('')
        assert_equals(self.func_call().text, '321')
        assert_equals(self.func_call('func2').text, '')
        
    def test_assert_has_calls(self):
        
        self.func_call()
        self.func_call(a=10)
        self.func_call(a=10, b=20)
        
        self.mock.assert_has_calls(call(),
                              call(a=10),
                              call(a=10, b=20))
        
        self.mock.assert_has_calls(call(a=10),
                              call(a=10, b=20),
                              check_call_count=False)    
    
    def test_assert_number_of_calls(self):
        
        assert_raises_regexp(AssertionError,
                             "func not called at all",
                             self.mock.func.assert_called)        
        
        self.mock.func.assert_not_called()
        
        self.func_call()
        
        self.mock.func.assert_called()
        
        self.mock.func.assert_called_once()
        self.func_call()
        
        assert_raises_regexp(AssertionError,
                             "func called 2 times \(1 expected\)",
                             self.mock.func.assert_called_once)        
        
        self.mock.func.assert_called_n_times(2)
        self.func_call()
        
        self.mock.func.assert_called_n_times(3)
        
        assert_raises_regexp(AssertionError,
                             "func called 3 times \(33 expected\)",
                             self.mock.func.assert_called_n_times,
                             33)
    
    def func_call(self, func='func', **kwargs):
        return http_call(self.mock, func, **kwargs)
