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

import functools
from inspect import isclass

from rmock.config import get_config

class Patch(object):
    
    def __init__(self, run_manager, *mock_args, **mock_kwargs):
        self.run_manager = run_manager
        self.mock_args = mock_args
        self.mock_kwargs = mock_kwargs
        self._context_manager_mock = None
        
        self.classvar = mock_kwargs.pop('classvar', None)
    
    def __call__(self, test_object):
                
        if isclass(test_object):
            test_class = test_object
            mock = self.run_manager.run(*self.mock_args, **self.mock_kwargs)
            
            if self.classvar is not None:
                setattr(test_class, self.classvar, mock) 
            
            for function_name, test_function in self._list_test_functions(test_class):
                wrapped = self._make_function_wrapper(test_function, mock)
                setattr(test_class, function_name, wrapped)
            
            return test_class
        else:
            if self.classvar is not None:
                raise TypeError("classvar supported only for class decorator")
            
            test_function = test_object
            
            @functools.wraps(test_function)
            def wrapped(function_self, *args, **kwargs):
                
                mock = self.run_manager.run(*self.mock_args, **self.mock_kwargs)                
                
                try:
                    return test_function(function_self, mock, *args, **kwargs)
                finally:
                    mock.finalize()
            
            return wrapped
    
    def _make_function_wrapper(self, test_function, mock):
        
        @functools.wraps(test_function)
        def wrapped(function_self, *args, **kwargs):
            
            func_args = list(args)
            if self.classvar is None:
                func_args.insert(0, mock)
            
            func_kwargs = kwargs
            
            try:
                return test_function(function_self, *func_args, **func_kwargs)
            finally:
                mock.reset_mock()
                mock.start_server()
        
        return wrapped
    
    def _list_test_functions(self, test_class):
        
        test_method_prefix = get_config()['test_method_prefix']
        
        for attr in dir(test_class):
            if not attr.startswith(test_method_prefix):
                continue
            
            attr_value = getattr(test_class, attr)
            
            if not hasattr(attr_value, "__call__"):
                continue
            
            yield attr, attr_value
    
    def __enter__(self):
        self._context_manager_mock = self.run_manager.run(*self.mock_args, **self.mock_kwargs)
        return self._context_manager_mock
    
    def __exit__(self, *args):
        if self._context_manager_mock:
            self._context_manager_mock.finalize()
            self._context_manager_mock = None
