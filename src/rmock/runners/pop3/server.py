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

import sys
import logging
import socket

from SocketServer import StreamRequestHandler 
from SocketServer import TCPServer

logger = logging.getLogger("rmock.pop3")

class Pop3ServerImpl(object):
    
    def connect(self):
        pass
    
    def login(self, user, password):
        pass
        
    def uidl(self):
        pass
    
    def retr(self, uid):
        pass
    
    def top(self, uid):
        pass
        
    def dele(self, uid):
        pass
    
    def quit(self):
        pass           

class Pop3ProtocolError(Exception):
    
    def __init__(self, message):
        Exception.__init__(self, message)
        self.message = message
    
class Pop3RequestHandler(StreamRequestHandler):
    
    def handle(self):
        
        self.quitted = False
        self.impl = self.server.impl
        self.username = None
        self.password = None
        self.logged_in = False
        self.uid_mapping = {}        
        
        welcome = self.impl.connect()
        self._send_single_response(welcome)
        
        while not self.quitted:
            
            try:
                request = self.rfile.readline()
            except socket.error, e:
                logger.info('socket error: %s', e)
                return
            
            if request is None:
                break
            
            request = request.strip()
            funcname, params = self._parse_request(request)
            logger.debug("request: %s %s", funcname, params)
            
            handler_function = getattr(self, '_handle_%s' % funcname, None)
            if handler_function is not None:
                try:
                    handler_function(params)
                except Pop3ProtocolError, e:
                    logger.error("pop3 protocol error: %s", e)
                    self._send_error_response(e.message)
                except Exception:
                    logger.exception("internal error")
                    self._send_error_response("internal error")                    
            else:
                logger.warning("invalid fuction: %s", funcname)
                self._send_error_response('unknown command: %s' % funcname)
    
    def _handle_connect(self, params):
        
        welcome = self.impl.connect()
        self._send_single_response(welcome)
    
    def _handle_user(self, params):
        #<command name> <key> <flags> <exptime> <bytes> [noreply]\r\n        
        self.username, = self._checked_get_params(params, 1)
        self._send_single_response('')
    
    def _handle_pass(self, params):
        #<command name> <key> <flags> <exptime> <bytes> [noreply]\r\n        
        self.password, = self._checked_get_params(params, 1)
        self.logged_in = self.impl.login(self.username, self.password)
                
        if not self.logged_in:
            raise Pop3ProtocolError("auth error")
        
        result = 'connected :) '
        self._send_single_response(result)
    
    def _handle_uidl(self, params):
        
        self._verify_logged_in()
        uids = self.impl.uidl()
        uids_nr = list(enumerate(uids, 1))
        self.uid_mapping = {str(nr): uid for (nr, uid) in uids_nr}
        if len(params) > 0:
            nr = params[0]
            line = self._make_uid_line(nr, self.uid_mapping[nr])
            self._send_single_response(line)
        else:
            lines = [self._make_uid_line(nr, uid)
                     for (nr, uid) in uids_nr]
            self._send_multi_response('', lines)
    
    def _handle_retr(self, params):
        
        self._verify_logged_in()        
        nr, = self._checked_get_params(params, 1)
        
        uid = self._get_uid_for_number(nr)
        content = self.impl.retr(uid)
        header = '%s octets' % (len(content))
        self._send_multi_response(header, content)
    
    def _handle_top(self, params):
        
        self._verify_logged_in()        
        nr, = self._checked_get_params(params, 1)
        uid = self._get_uid_for_number(nr)
        
        content = self.impl.top(uid)
        self._send_multi_response('', content)
    
    def _handle_dele(self, params):
        
        self._verify_logged_in()        
        nr, = self._checked_get_params(params, 1)
        uid = self._get_uid_for_number(nr)
        
        content = self.impl.dele(uid)
        self._send_single_response('deleted') 
    
    def _handle_quit(self, params):
        response = self.impl.quit()
        self._send_single_response(response)
        self.quitted = True
    
    def _verify_logged_in(self):
        if not self.logged_in:
            raise Pop3ProtocolError("please log in")
    
    def _checked_get_params(self, params, count):
        if len(params) < count:
            raise Pop3ProtocolError("not enough params")
        
        return params[:count]
    
    def _get_uid_for_number(self, nr):
        
        if not self.uid_mapping:
            logger.warning("no uidl before retr")
            self._handle_uidl([])
        
        try:
            uid = self.uid_mapping[nr]
        except KeyError:
            raise Pop3ProtocolError('no such message')
        
        return uid
    
    def _make_uid_line(self, nr, uid):
        return ' '.join([str(nr), uid])
        
    def _send_get_response(self, key, value):
        #VALUE <key> <flags> <bytes> [<cas unique>]\r\n
        if value:        
            self._send_response('VALUE %s 0 %s' % (key, len(value)))
            self._send_response(value)
    
    def _send_response(self, message):
        #logger.info("response: %s", value)
        logger.debug("response: %s", message) 
        self.wfile.write(message + "\r\n")
    
    def _send_single_response(self, message):
        self._send_response('+OK %s' % message)
    
    def _send_multi_response(self, message, content):
        self._send_response('+OK %s' % message)
        if isinstance(content, basestring):
            content = content.splitlines()
        
        for line in content:
            self._send_response(line)
            
        self._send_response('.')
    
    def _send_error_response(self, message):
        self._send_response('-ERR %s' % message)
    
    def _parse_request(self, request):
        parts = request.split()
        
        if not parts:
            return '', []
        
        return parts[0].lower(), parts[1:]

class Pop3Server(TCPServer):
    
    #TODO: make ipv6 code more generic
    
    address_family = socket.AF_INET6
    allow_reuse_address = True    
    
    def __init__(self, impl, port):
        TCPServer.__init__(self, ('', port), Pop3RequestHandler)
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
                
        logger.debug("pop3 server error", exc_info=True)
