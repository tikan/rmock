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
from nose.tools import assert_true

from rmock.core import RmockData

def test_rmockdata_calls():
    
    rmock_data = RmockData()
    
    rmock_data.register_call('func', (1, 2, 3), {'a': 1})
    rmock_data.register_call('func', (3,), {'a': 1})
    
    assert_equals(rmock_data.get_calls('func2'), [])
    
    assert_equals(rmock_data.get_calls('func'),
                  [((1, 2, 3), {'a': 1}),
                   ((3,), {'a': 1})])
    
    assert_equals(rmock_data.get_calls(),
                    [('func', (1, 2, 3), {'a': 1}),
                     ('func', (3,), {'a': 1})])
    
    call = rmock_data.get_calls()[0]
    
    assert_equals(call.funcname, 'func')
    assert_equals(call.args, (1, 2, 3))
    assert_equals(call.kwargs, {'a': 1})

def test_rmockdata_results():

    rmock_data = RmockData()
    
    rmock_data.set_result('func', 'func_result')
    
    assert_equals(rmock_data.get_result('func'), 'func_result')
    assert_equals(rmock_data.get_result('func', (20,), dict(a=30)), 'func_result')
    
    rmock_data.set_result_with_params('func', 'func_result_spec', (20,), {'a': 30})
        
    assert_equals(rmock_data.get_result('func', (20,), dict(a=30)), 'func_result_spec')
    
    assert_equals(rmock_data.get_result('func22', (20,), dict(a=30)), None)
    
    assert_equals(rmock_data.get_result('func22', (20,), dict(a=30)), None)
    
    rmock_data.set_result('func3', 'generic')
    rmock_data.set_result_with_params('func3', 'no args', (), {}, )
    rmock_data.set_result_with_params('func3', 'one arg', (), {'a': 10}, )
    
    assert_equals(rmock_data.get_result('func3'), 'no args')
    assert_equals(rmock_data.get_result('func3', (), dict(a=10)), 'one arg')
    assert_equals(rmock_data.get_result('func3', (), dict(a=10, b=20)), 'generic')

def test_rmockdata_result_replace():
    
    rmock_data = RmockData()
    
    rmock_data.set_result('func', 'func_result1')
    assert_equals(rmock_data.get_result('func'), 'func_result1')
    
    rmock_data.set_result('func', 'func_result2')
    assert_equals(rmock_data.get_result('func'), 'func_result2')
    
    assert_equals(len(rmock_data.get_all_results('func')), 1)
    
    rmock_data.set_result_with_params('func2', 'func2_result1', (), {'a': 10})
    assert_equals(rmock_data.get_result('func2', None, {'a': 10}), 'func2_result1')
    
    rmock_data.set_result_with_params('func2', 'func2_result2', (), {'a': 10})
    assert_equals(rmock_data.get_result('func2', None, {'a': 10}), 'func2_result2')
    assert_equals(len(rmock_data.get_all_results('func2')), 1)

def test_rmockdata_calls_and_results():
    rmock_data = RmockData()
    
    rmock_data.set_result('myf', 123)
    rmock_data.set_result_with_params('myf', 213, ('s',), {'z': 11})
    
    assert_equals(rmock_data.register_call_and_get_result('myf', ('x',), {}),
                  123)
    
    assert_equals(rmock_data.register_call_and_get_result('myf', ('s',), {'z': 11}),
                  213)
    
    assert_equals(rmock_data.get_calls('myf'), [(('x',), {}),
                                                (('s',), {'z': 11})])
    
def test_rmockdata_default_return_value():
    
    rmock_data = RmockData()
    
    assert_equals(rmock_data.get_result('func'), None)
    rmock_data.set_default_result(123)
    assert_equals(rmock_data.get_result('func'), 123)
    rmock_data.set_default_result(None)
    assert_equals(rmock_data.get_result('func'), None)
    
    rmock_data.set_default_result(123)    
    rmock_data.set_result('func', 444)
    assert_equals(rmock_data.get_result('func'), 444)
    assert_equals(rmock_data.get_result('func2'), 123)
