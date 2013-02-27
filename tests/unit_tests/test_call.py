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
from nose.tools import assert_true

from rmock import call
from rmock import call_subset
from rmock import params_subset

def test_call_simple():
    assert_equals(call(), call())
    assert_equals(call('a', b=20), call('a', b=20))
    
    assert_not_equals(call(b=20), call('a', b=20))
    assert_not_equals(call('a', b=20), call('a', b='20'))
    
def test_call_with_params_subset():
    assert_equals(call(params_subset()),
                  call(params_subset()))
    
    assert_equals(call(params_subset(a=10)),
                  call(params_subset(a=10, b=20)))
    
    assert_not_equals(call(params_subset(a=10, b=30)),
                      call(params_subset(a=10, b=20)))
def test_call_subset():
    assert_equals(call_subset(), call_subset(),)
    
    assert_equals(call_subset(a=10),
                  call_subset(a=10, b=20))
    
    assert_not_equals(call_subset(a=10, b=30),
                      call_subset(a=10, b=20))
