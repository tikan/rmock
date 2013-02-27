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

from tornado.web import Application

import logging

from rmock.runners.http.proxy.handler import ProxyMockHttpHandler
from rmock.runners.http import HttpRunner

logger = logging.getLogger("rmock.http-proxy")

class HttpProxyRunner(HttpRunner):
    
    def __init__(self,
         childs,
         child_chooser,
         protocol=None,
         protocol_args=None,
         port=None,
         slug='',
         url=None
    ):
        super(HttpProxyRunner, self).__init__(
            port=port, slug=slug, url=url,
            protocol=protocol,
            protocol_args=protocol_args,
        )
        self.childs = childs
        self.child_chooser = child_chooser
    
    def run(self, rmock_data):
                
        logger.info("http server start; listening on port=%s, slug=%s",
                    self.port, self.slug)
        
        url_regexp = self._make_url_regexp()
        application = Application([(
            url_regexp,
            ProxyMockHttpHandler,
            dict(
                rmock_data=rmock_data,
                protocol_class=self.protocol_class,
                protocol_args=self.protocol_args,
                slug=self.slug,
                childs=self.childs,
                child_chooser=self.child_chooser
            )
        )])
        
        self._run_tornado_server(application)
    
    def add_child(self, child):
        self.childs.append(child)
    
    def __str__(self):
        return "http-proxy(port=%s slug=%s childs=%s)" % \
            (self.port, self.slug, self.childs)
