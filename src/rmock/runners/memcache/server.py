# coding=utf

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

import sys
import logging
import socket

from SocketServer import StreamRequestHandler
from SocketServer import ThreadingMixIn
from SocketServer import TCPServer


#http://code.sixapart.com/svn/memcached/trunk/server/doc/protocol.txt

logger = logging.getLogger("rmock.memcache")

class MemcacheServerImpl(object):
    
    def get(self, key):
        pass
    
    def set(self, key, value, time):
        pass

    def delete(self, key):
        pass

class MemcacheRequestHandler(StreamRequestHandler):
    
    def handle(self):
        
        self.quitted = False
        self.impl = self.server.impl
               
        while not self.quitted:
            
            try:
                request = self.rfile.readline()
            except socket.error, e:
                logger.info('socket error: %s', e)
                return
            
            logger.debug("raw request: '%s'", request)
            if not request:
                break
            
            request = request.strip()
            funcname, params = self._parse_request(request)
            logger.debug("request: %s %s", funcname, params)
            
            handler_function = getattr(self, 'handle_memcache_%s' % funcname, None)
            if handler_function is not None:
                handler_function(params)
            else:
                logger.warning("invalid fuction: %s", funcname)
                self._send_response('ERROR')
    
    def handle_memcache_stats(self, params):
        
        #TODO: real stats support
        self._send_response('STAT version 1.4.5')
        self._send_response('END')    
    
    def handle_memcache_get(self, params):
        keys = params
        
        for key in keys:
            value = self.impl.get(key)                
            self._send_get_response(key, value or '')
        
        self._send_response('END')
    
    def handle_memcache_set(self, params):
        #<command name> <key> <flags> <exptime> <bytes> [noreply]\r\n        
        key, _, exptime, size = params[:4]
        value = self.rfile.read(int(size) + 2).rstrip()
        
        exptime = int(exptime)
        
        set_result = self.impl.set(key, value, time=exptime)
        
        result = 'STORED' if set_result else 'NOT_STORED'
        
        self._send_response('%s' % result)
        
    def handle_memcache_delete(self, params):
        key = params[0]
        del_result = self.impl.delete(key)
                
        result = 'DELETED' if del_result else 'NOT_FOUND'
        
        self._send_response(result)
    
    def handle_memcache_quit(self, params):
        self.quitted = True
    
    def _send_get_response(self, key, value):
        #VALUE <key> <flags> <bytes> [<cas unique>]\r\n
        if value:        
            self._send_response('VALUE %s 0 %s' % (key, len(value)))
            self._send_response(value)
    
    def _send_response(self, value):
        logger.debug("response: %s", value) 
        self.wfile.write(value + "\r\n")
    
    def _parse_request(self, request):
        parts = request.split()
        
        if not parts:
            return '', []
        
        return parts[0], parts[1:]

class MemcacheServer(ThreadingMixIn, TCPServer):
    
    address_family = socket.AF_INET6
    
    def __init__(self, port, impl):
        TCPServer.__init__(self, ('', port), MemcacheRequestHandler)
        self.impl = impl
    
    def server_bind(self):
        # Override this method to be sure v6only is false: we want to
        # listen to both IPv4 and IPv6!
        self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, False)
        TCPServer.server_bind(self)        
    
    def handle_error(self, request, client_address):
        
        etype = sys.exc_info()[0]
        if etype is SystemExit:
            raise
        
        logger.debug("memcache server error", exc_info=True)
    
    allow_reuse_address = True
