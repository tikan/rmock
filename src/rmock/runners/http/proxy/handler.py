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

from rmock.runners.http.handler import MockHttpHandler
from rmock.runners.http.handler import with_exception_handling

from rmock.core.call import Call
from rmock.runners.http.handler import HttpCode

logger = logging.getLogger("rmock.http-proxy")

class ProxyMockHttpHandler(MockHttpHandler):
    
    @with_exception_handling
    def initialize(self,
                   rmock_data,
                   protocol_class,
                   protocol_args,
                   slug,
                   childs,
                   child_chooser):
        
        super(ProxyMockHttpHandler, self).initialize(
            rmock_data,
            protocol_class,
            protocol_args,
            slug
        )
        
        self.childs = childs
        self.child_chooser = child_chooser
    
    def _process_function_call_impl(self, funcname, args, kwargs, headers):
        
        data = Call._make(funcname=funcname,
                          args=args,
                          kwargs=kwargs,
                          headers=headers)
        
        mock = self.child_chooser(data, self.childs)
        
        if mock is None:
            logger.info("404: matching mock not found")
            return HttpCode(404)
        
        logger.info("proxying request to: %s", mock.name)
        return mock._rmock_data.register_call_and_get_result(
            funcname, args, kwargs,
            headers=headers
        )
