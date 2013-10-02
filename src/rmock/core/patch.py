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

    """
    Decorator or context manager which injects properly configured mock into the current context.

    If Patch is used as a method decorator than it a mock is created before each method call,
    injected as a first parameter and than finalized after the method returns.
    If it's used as a class decorator than a mock is created on class definition and it's
    reused in all test method calls, just being resetted before each call. Be default
    the mock objects is passed as a first argument to each method.
    If you want the mock to be stored in class-level attribute instead than pass the attribute name
    as a `classvar` attribute to `Patch` __init__ method.
    This class could also be used as a context manager - in this case mock object is created and returned
    from __enter__ method and finalized in __exit__ method.

    In that moment `Patch` decorator doesn't work for free (non-method) functions, it should be
    considered as a bug and will be fix in the future. You could use context manager
    around whole function body instead for now.

    Additionally, because of the way in which class decorators work in python subclasses of a class decorated
    with `Patch` wouldn't have its test methods wrapped with reset_mock calls.
    The simple workaround for this problem is to manually call reset_mock in setup method in the base class.
    Note that in future that behaviour may be changed.
    """

    def __init__(self, run_manager, *mock_args, **mock_kwargs):
        """
        Initialize Patch object with given attributes

        The `args` and `kwargs` and generally the same
        """
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
