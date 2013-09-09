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

import pprint

from rmock.tools import len_trim_dict

from rmock.core.call import Call

from rmock.core.subset import ParamsSubset
from rmock.core.subset import DictSubset

from rmock.config import get_config

conf = get_config()

class RmockFunctionProxy(object):
    
    def __init__(self, parent_rmock, funcname):
        self.args = None
        self.kwargs = None
        self.with_params = False
        self.funcname = funcname
        self.parent_rmock = parent_rmock
        self.rmock_data = self.parent_rmock.get_rmock_data()
    
    def assert_called(self):
        if self.calls_count == 0:
            raise AssertionError("%s not called at all" % self.funcname)
        
    def assert_called_n_times(self, n):
        if self.calls_count != n:
            raise AssertionError("%s called %s times (%s expected)" 
                                 % (self.funcname, self.calls_count, n))    
    
    def assert_called_once(self):
        self.assert_called_n_times(1)    
    
    def assert_called_with(self, *args, **kwargs):
        args, kwargs = self._get_call_params(args, kwargs)
        func_calls = self.calls
        
        if not func_calls:
            raise AssertionError("%s not called at all" % self.funcname)
        
        expected_calls = (args, kwargs)
        
        if expected_calls not in func_calls:
            
            raise AssertionError("invalid %s call;\n expected: %s;\n got: %s" % (
                self.funcname,
                pprint.pformat(len_trim_dict(expected_calls)),
                pprint.pformat(len_trim_dict(map(Call._to_tuple, func_calls))))
            )
    
    def assert_called_once_with(self, *args, **kwargs):
        self.assert_called_with(*args, **kwargs)
        self.assert_called_once()
    
    def assert_has_calls(self, calls, check_call_count=True):
        if check_call_count and len(calls) != len(self.calls):
            raise AssertionError("%s called invalid number of times; expected: %s;\n got: %s" 
                                 % (self.funcname, len(calls), len(self.calls)))
        
        for call in calls:
            self.assert_called_with(*call.args, **call.kwargs)
    
    def assert_not_called(self, *args, **kwargs):
        call_count = len(self.calls)
        
        if call_count != 0:
            raise AssertionError("%s was unexpectedly called (%s times)" % 
                                 (self.funcname, call_count))  
    
    def assert_not_called_with(self, *args, **kwargs):
        func_calls = self.calls
        
        expected_calls = (args, kwargs)
        call_count = func_calls.count(expected_calls)
        
        if call_count != 0:
            raise AssertionError("%s was unexpectedly called with desired arguments (%s times)" % 
                                 (self.funcname, call_count))        
    
    @property
    def calls(self):
        return self.rmock_data.get_calls(self.funcname)
    
    @property
    def calls_count(self):
        return len(self.calls)
    
    @property
    def called(self):
        return len(self.calls) > 0
    
    @property
    def return_value(self):
        return self.rmock_data.get_result(self.funcname, self.args, self.kwargs)
    
    @return_value.setter
    def return_value(self, result):
        if self.with_params: 
            self.rmock_data.set_result_with_params(self.funcname, result, self.args, self.kwargs)
        else:
            self.rmock_data.set_result(self.funcname, result)
    
    side_effect = return_value
    
    def __call__(self, *args, **kwargs):
        self.with_params = True
        self.args, self.kwargs = self._get_call_params(args, kwargs)
              
        return self
    
    def _get_call_params(self, args, kwargs):
        if len(args) == 1 and not kwargs and isinstance(args[0], ParamsSubset):
            sbs = args[0]
            return sbs.args, DictSubset(sbs.kwargs)
        else:
            return args, kwargs
