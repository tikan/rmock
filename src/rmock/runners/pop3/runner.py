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
from rmock.runners.runner import RmockRunner

from rmock.core import RmockData
from rmock.errors import RmockParamsError
from rmock.tools.net import find_port
from rmock.runners.pop3.server import Pop3Server
from rmock.runners.pop3.server import Pop3ProtocolError

logger = logging.getLogger("rmock.memcache")

from rmock.tools import len_trim
from rmock.tools import len_trim_dict

class Pop3ServerMockImpl(object):
    
    WELCOME_MESSAGE = "welcome to rmock pop3 server"
    GOODBYE_MESSAGE = "ok, sayonara"
    
    def __init__(self, rmock_data):
        self.rmock_data = rmock_data
        
    def connect(self):
        result = self._process_function_call('get_welcome', (), {})
        return result or self.WELCOME_MESSAGE
    
    def login(self, user, password):
        result = self._process_function_call('login', (user, password), {})
        return True if result else False
        
    def uidl(self):
        result = self._process_function_call('uidl', (), {})
        return result or []
    
    def retr(self, uid):
        result = self._process_function_call('retr', (uid,), {})
        
        if result is None:
            raise Pop3ProtocolError("no such message")
        
        return result
    
    def top(self, uid):
        result = self._process_function_call('top', (uid,), {})
        
        if result is None:
            raise Pop3ProtocolError("no such message")        
        
        return result
        
    def dele(self, uid):
        result = self._process_function_call('dele', (uid,), {})
        return result
        
    def quit(self):
        result = self._process_function_call('quit', (), {})
        return result or self.GOODBYE_MESSAGE
    
    def _process_function_call(self, funcname, args, kwargs):
        
        logger.info("call: funcname=%s args=%s kwargs=%s", 
            len_trim(funcname),
            len_trim_dict(list(args)),
            len_trim_dict(kwargs)
        )
        
        return self.rmock_data.register_call_and_get_result(funcname, args, kwargs)

class Pop3Runner(RmockRunner):
    
    def __init__(self, port=None):
        RmockRunner.__init__(self)
        
        # random port support
        port = find_port(port)
        
        self.port = port
        self.run_params.update(port=port)
        
    def run(self, rmock_data):
        
        logger.info("pop3 server start; listening on port=%s", self.port)
        
        impl = Pop3ServerMockImpl(rmock_data)
        server = Pop3Server(port=self.port, impl=impl)
        server.serve_forever()

    def __str__(self):
        return "pop3(port=%s)" % self.port
