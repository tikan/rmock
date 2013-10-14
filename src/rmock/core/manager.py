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

import multiprocessing.managers

from rmock.runners.http.runner import HttpRunner
from rmock.runners.http.proxy.runner import HttpProxyRunner
from rmock.runners.smtp.runner import SmtpRunner
from rmock.runners.memcache.runner import MemcacheRunner
from rmock.runners.pop3.runner import Pop3Runner
from rmock.runners.lmtp.runner import LmtpRunner

from rmock.core import RmockData
from rmock.core import Rmock
from rmock.core.patch import Patch

from rmock.errors import RmockError

import rmock.config

class RmockProcessManager(multiprocessing.managers.SyncManager):
    pass

RmockProcessManager.register('RmockData', RmockData)

logger = logging.getLogger("rmock.manager")

class RmockRunManager(object):

    _runners = {'http': HttpRunner,
                'smtp': SmtpRunner,
                'lmtp': LmtpRunner,
                'http-proxy': HttpProxyRunner,
                'memcache': MemcacheRunner,
                'pop3': Pop3Runner}
    
    def __init__(self):
        self._mocks = {}
        self._process_manager = None
        self._logger = None
    
    def get(self, key):
        return self._mocks[key]
    
    def create(self,
               runner='http',
               *args,
               **kwargs):
        name = kwargs.pop('key', None) or kwargs.pop('name', None)
        spec = kwargs.pop('spec', None) or kwargs.pop('config', None)
        autospec = kwargs.pop('autospec', None)
                
        mock = self._mocks.get(name)
        
        if mock is not None:
            return mock
        
        # TODO: one manager per application
        #if self._process_manager is None:
        self._process_manager = RmockProcessManager()
        self._process_manager.start()
        
        if isinstance(runner, basestring):
            runner = self._runners[runner]
        
        rmock_data = self._process_manager.RmockData()
        
        runner_obj = runner(*args, **kwargs)
        runner_obj.mock_name = name
        
        if isinstance(spec, type):
            spec = spec()
        
        mock = Rmock(runner_obj,
                     rmock_data,
                     name=name,
                     spec=spec,
                     autospec=autospec)
        if name is not None:
            self._mocks[name] = mock
        
        return mock
    
    def run(self,
            runner='http',
            *args,
            **kwargs):
        mock = self.create(runner, *args, **kwargs)
        mock.start_server() 
        
        return mock
    
    def patch(self, *mock_args, **mock_kwargs):
        return Patch(self, *mock_args, **mock_kwargs)
    
    def register_remote(self, class_, name=None):
        if name is None:
            name = class_.__name__
        
        RmockProcessManager.register(name, class_)
    
    def create_remote(self, cls, *args, **kwargs):
        remote_cls = getattr(self._process_manager, cls.__name__)
        return remote_cls(*args, **kwargs)
    
    def configure(self, **kwargs):
        conf = rmock.config.get_config()
        for key in kwargs:
            if key not in kwargs:
                raise RmockError("unknown config item: %s" % key)
        
        conf.update(**kwargs)
    
    def enable_logging(self,
                       level=logging.INFO,
                       handler=None,
                       format_="%(name)s[%(process)s] %(message)s"):
        if isinstance(level, basestring):
            level = level.upper()
        
        handler = handler or logging.StreamHandler()
        
        level = getattr(logging, level.upper()) if isinstance(level, basestring) else level
        self._logger = logging.getLogger("rmock")
        self._logger.setLevel(level)
        
        formatter = logging.Formatter(format_)
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)
    
    def get_logger(self):
        return self._logger
