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
import signal
import time

from multiprocessing import Process

#import multiprocessing
#multiprocessing.log_to_stderr()

from rmock.core import RmockFunctionProxy
from rmock.errors import RmockStartError

from rmock.tools import attr_dict

logger = logging.getLogger("rmock.core")

class Rmock(object):
    
    def __init__(self,
                 runner,
                 rmock_data,
                 name=None,
                 spec=None,
                 autospec=False):
        
        self._runner = runner
        self._rmock_data = rmock_data #self._rmock_manager.RmockData()
        self._spec = spec
        self._runner_proccess = None
        self._autospec = autospec
        
        self.name = name
        
        if self._spec:
            self._spec.add_modified_callback(self.apply_spec)
            self.apply_spec()
        
        self._server_started = False
        
    def __getattr__(self, name):
        return RmockFunctionProxy(self, name)
    
    def get_all_calls(self):
        return self._rmock_data.get_calls()
    
    def reset_mock(self):
        self._rmock_data.reset()
        if self._spec:
            self._spec.reset()
    
    #TODO: remove
    reset = reset_mock
    
    def reset_calls(self):
        self._rmock_data.reset_calls()
    
    def freeze_mock(self):
        self._rmock_data.freeze()
    
    def finalize(self):
        self.stop_server()
    
    def apply_spec(self):
        self.reset_mock()
        self._spec.apply(self)
        
        if self._autospec:
            self.freeze_mock()        
    
    def get_spec(self):
        return self._spec
    
    def get_rmock_data(self):
        return self._rmock_data
    
    def set_default_return_value(self, result):
        self._rmock_data.set_default_result(result)
    
    set_default_side_effect = set_default_return_value
    
    def join_server(self):
        self._runner_proccess.join()
        
    def start_server(self):
        
        if self._server_started:
            logger.debug("server already started; ignoring")
            return
        
        if self._runner_proccess is None:
            self._runner_proccess = Process(target=self._run_mock_process)
            self._runner_proccess.daemon = True
        else:
            raise RmockStartError("server process (%s) already running" % self.runner_params)
        
        self._runner_proccess.start()
        
        #TODO: some code to check whether the server has successfully started in better way
        time.sleep(.1)
        
        if not self._runner_proccess.is_alive():
            raise RmockStartError("error starting server process (%s)" 
                                  % self.runner_params)
        
        self._server_started = True
    
    def stop_server(self):
        
        if self._runner_proccess is not None:
            logger.debug("terminating process %s", self._runner_proccess.pid)
            self._runner_proccess.terminate()
            self._runner_proccess = None
            self._server_started = False
    
    @property
    def runner_params(self):
        result = attr_dict(type=type(self._runner).__name__)
        
        result.update({key: value for key, value in self._runner.run_params.iteritems()
                       if value is not None})
        
        return result
    
    def _run_mock_process(self):
        signal.signal(signal.SIGTERM, self._runner.handle_signal)
        signal.signal(signal.SIGINT, self._runner.handle_signal)
        
        self._runner.run(self._rmock_data)    
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.finalize()
    
    def __del__(self):
        self.finalize()
        
    def __str__(self):
        return "rmock(name=%s runner=%s)" % (self.name or '', self._runner)
    
    __repr__ = __str__
