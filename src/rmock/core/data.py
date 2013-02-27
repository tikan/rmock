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

from types import FunctionType

from rmock.core.call import Call
from rmock.errors import InvalidFunction

class RmockData(object):
    """
    Data container which stores results defined by client and responses registered on server
    
    Important attributes:
    calls: list of Call objects, each of them has function name and params (args, kwargs)
    
    results: dict mapping function name to list of (params, result) tuples. 
        TODO: describe matching algorithm
        TODO: maybe default results for each function should be stored in separate attribute
    
    Server code should use register_call_and_get_result, client code generally should use set_result
    
#{
    'calls': [Call(('f1', 'sss', {})),
              Call('f2': 'xxx', {'a': 10}))],
    
     'results': {'f1': [
                            (((), {}), 'result'),
                            (None, 'result222') 
                        ]
             }
}    
    
    """    
    def __init__(self):
        self.calls = []
        self.results = {}
        self.default_result = None
        self.frozen = False
    
    def get_calls(self, funcname=None):
        """
        Return list of all calls of given function  
        """
        if funcname is None:
            return self.calls
        
        return [call_ for call_ in self.calls
                if call_.funcname == funcname]
    
    def register_call(self, funcname, args, kwargs, headers=None):
        """
        Register call of given function with given params; should be used in server code
        
        @param funcname: name of called function
        @param args: list of positional arguments
        @param kwarsg: list of keyword arguments
        @param headers: optional list of call headers
        """
        
        self._verify_call_allowed(funcname, args, kwargs)        
        
        self.calls.append(Call._make(funcname=funcname,
                                     args=args,
                                     kwargs=kwargs,
                                     headers=headers))
    
    def get_result(self, funcname, args=None, kwargs=None):
        """
        Return result for given call
        
        The first matching call is returned. 
        @param funcname: name of called function
        @param args: optional list of positional arguments
        @param kwargs: optional list of keywords arguments
        """
        
        self._verify_call_allowed(funcname, args, kwargs)
        
        args = args or ()
        kwargs = kwargs or {}
        
        func_results = self.results.get(funcname)
        
        if func_results is None:
            return self._make_default_result(*args, **kwargs)
        
        for (result_params, result) in reversed(func_results): 
            
            if result_params is None:
                return self._make_result(result, *args, **kwargs)
            
            result_args, result_kwargs = result_params
            
            if result_args == args and result_kwargs == kwargs:
                return self._make_result(result, *args, **kwargs)
        
        return self._make_default_result(*args, **kwargs)
    
    def get_all_results(self, funcname):
        func_results = self.results.get(funcname)
        return func_results
    
    def register_call_and_get_result(self, funcname, args, kwargs, headers=None):
        
        self.register_call(funcname, args, kwargs, headers)
        return self.get_result(funcname, args, kwargs)    
    
    def set_default_result(self, result):
        """
        Set default call result, which is used in case of unmatched call 
        """
        self.default_result = result
    
    def set_result(self, funcname, result):
        """
        Set default result of function call
        
        @param funcname: name of function
        @param result: result of function call
        """
        
        self.set_result_with_params(funcname, result, None, None)    
    
    def set_result_with_params(self, funcname, result, args, kwargs):
        """
        Set default of function call with specified params
        
        @param funcname: name of function
        @param result: result of function call
        @param args: positional arguments which should be matched
        @param kwargs: positional arguments which should be matched
        """
        
        assert (args is None and kwargs is None) or \
            (isinstance(args, tuple) and isinstance(kwargs, dict))
        
        self._verify_call_allowed(funcname, args, kwargs)        
        
        if args is not None or kwargs is not None:
            result_params = (args or (), kwargs or {})
        else:
            result_params = None
        
        func_results = self.results.get(funcname, [])
        
        self._remove_current_result(func_results, result_params)
        
        func_results.append((result_params, result))
        
        self.results[funcname] = func_results
    
    def reset(self):
        """
        Reset all calls and results
        """
        self.reset_calls()
        self.results = {}
        self.frozen = False
    
    def reset_calls(self):
        """
        Reset all calls
        """
        self.calls = []
    
    def freeze(self):
        self.frozen = True
    
    def _verify_call_allowed(self, funcname, args, kwargs):
                        
        if self.frozen and funcname not in self.results:
            raise InvalidFunction("Function %s not allowed" % funcname)
    
    def _remove_current_result(self, func_results, result_params):
        
        current_result = next(((params, result)
            for (params, result) in func_results if params == result_params),
            None
        )
        
        if current_result is not None:
            func_results.remove(current_result)
    
    def _make_default_result(self, *args, **kwargs):
        return self._make_result(self.default_result, *args, **kwargs)
    
    def _make_result(self, result, *args, **kwargs):
        
        if hasattr(result, '__call__'):
            return result(*args, **kwargs)
        
        return result
    
    def __str__(self):
        return 'rmock_data(calls=%s, results=%s)' % (self.calls, self.results)
    
    __repr__ = __str__
