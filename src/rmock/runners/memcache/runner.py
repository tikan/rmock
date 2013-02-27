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

import copy

from rmock.tools import len_trim
from rmock.tools import len_trim_dict

from rmock.runners.runner import RmockRunner

from rmock.runners.memcache.server import MemcacheRequestHandler
from rmock.runners.memcache.server import MemcacheServer

from rmock.core import RmockData
from rmock.errors import RmockParamsError
from rmock.tools.net import find_port

logger = logging.getLogger("rmock.memcache")

class MemcacheServerMockImpl(object):
    
    def __init__(self, rmock_data):
        
        #FIXME: copy becaouse of thread safety issue
        self.rmock_data = copy.copy(rmock_data)

    def get(self, key):
        result = self._process_function_call('get', (key,), {})
        return result

    def set(self, key, value, time):
        result = self._process_function_call('set', (key, value), {'time': time})
        
        if result is not None:
            return result
        
        return True

    def delete(self, key): 
        result = self._process_function_call('delete', (key,), {})
        
        if result is not None:
            return result
        
        return True

    def _process_function_call(self, funcname, args, kwargs):
        
        logger.info("call: funcname=%s args=%s kwargs=%s", 
            len_trim(funcname),
            len_trim_dict(list(args)),
            len_trim_dict(kwargs)
        )
        
        return self.rmock_data.register_call_and_get_result(funcname, args, kwargs)

class MemcacheRunner(RmockRunner):
    
    def __init__(self, port=None, url=None):
        RmockRunner.__init__(self)
        
        if url is not None:
            if port is not None:
                raise RmockParamsError("url must be only param")
            
            port = self._get_port_from_url(url)
        
        # random port support
        port = find_port(port)
        
        self.port = port
        self.run_params.update(port=port)
    
    def _get_port_from_url(self, url):
        hosts = url.split(',')
        if len(hosts) > 1:
            raise RmockParamsError("only one host mode supported for memcache")
        
        host, port = hosts[0].split(':')
        
        if host not in ("localhost", "127.0.0.1"):
            raise RmockParamsError("invalid url: %s; host must be localhost" % url)
        
        try:
            return int(port)
        except ValueError:
            raise RmockParamsError("port must be integer")
        
    def run(self, rmock_data):
        
        logger.info("memcache server start; listening on port=%s", self.port)
        impl = MemcacheServerMockImpl(rmock_data)    
        server = MemcacheServer(port=self.port, impl=impl)
        server.serve_forever()

    def __str__(self):
        return "memcache(port=%s)" % self.port
