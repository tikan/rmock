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

import re
import os
from functools import partial
import time
import logging
from urlparse import parse_qs
from urlparse import urlparse

from tornado.web import Application
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from rmock.runners.runner import RmockRunner
from rmock.runners.http.protocols import JsonRPCProtocol
from rmock.runners.http.protocols import CsProtocol
from rmock.runners.http.protocols import RawProtocol
from rmock.runners.http.handler import MockHttpHandler
from rmock.errors import RmockParamsError

from rmock.runners.http.handler import HttpCode
from rmock.runners.http.handler import HttpCodeError

from rmock.tools.net import find_port

logger = logging.getLogger("rmock.http")

class HttpRunner(RmockRunner):
    
    _protocols = {
        'jsonrpc': JsonRPCProtocol,
        'cs': CsProtocol,
        'raw': RawProtocol
    }
    
    _url_pattern = 'http://localhost:{port}/{slug}'
    
    def __init__(self,
                 port=None,
                 url_prefix='',
                 slug='',
                 protocol=None,
                 protocol_args=None,
                 url=None):
        
        RmockRunner.__init__(self)
        
        slug = url_prefix or slug
                                
        if url is not None:
            if port is not None or slug:
                raise RmockParamsError("url must be only param")
            
            port, slug = self._parse_url(url)
        else:
            port = find_port(port)            
            url = self._url_pattern.format(port=port, slug=slug)
        
        self.port = port
        
        if isinstance(protocol, basestring):
            self.protocol_class = self._protocols[protocol]
        else:
            self.protocol_class = protocol
        
        self.protocol_class = self.protocol_class or RawProtocol
        self.protocol_args = protocol_args
        
        self.slug = slug
        
        self.run_params.update(
            port=port,
            slug=slug,
            url=url,
        )
        
    def _parse_url(self, url):
        
        if not url.startswith("http://"):
            url = "http://" + url
        
        parsed_url = urlparse(url)        
        if parsed_url.hostname not in ("localhost", "127.0.0.1"):
            raise RmockParamsError("invalid url: %s; host must be localhost" % url)
        
        port = parsed_url.port or 80
        slug = parsed_url.path.lstrip('/')
        
        return port, slug
    
    def run(self, rmock_data):
                
        logger.info("http server start; listening on port=%s, slug=%s",
                    self.port, self.slug)
        
        url_regexp = self._make_url_regexp()
        application = Application([(
            url_regexp,
            MockHttpHandler,
            dict(
                rmock_data=rmock_data,
                protocol_class=self.protocol_class,
                protocol_args=self.protocol_args,
                slug=self.slug
            )
        )])
        
        self._run_tornado_server(application)
    
    def _run_tornado_server(self, application):
        http_server = HTTPServer(application)
        http_server.bind(self.port)
        http_server.start(1)

        ioloop = IOLoop.instance()
        ioloop.start()   
    
    def _make_url_regexp(self):
        url_re = ''.join(["/", self.slug, '.*'])
        return url_re.replace('//', '/')
    
    def __str__(self):
        return "http(port=%s slug=%s)" % (self.port, self.slug)
