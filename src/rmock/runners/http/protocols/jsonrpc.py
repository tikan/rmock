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
import json

from rmock.errors import RmockError

logger = logging.getLogger("rmock.jsonrpc")

#TODO: better error handling

#TODO: inherit from generic RPCError?

class JsonRPCError(RmockError):
    def __init__(self, message, code=-32700):
        RmockError.__init__(self, message, code)
        
        self.message = message
        self.code = code

class JsonRPCProtocol(object):
    
    def __init__(self):
        self.request_id = None
    
    def loads(self, method, url, body):
        
        if method != 'post':
            raise JsonRPCError("unsupported http method: %s" % method)
        
        parsed_params = json.loads(body)
        logger.debug("parsed params: %s", parsed_params)
        
        if isinstance(parsed_params, list):
            parsed_params = parsed_params[0]
                
        self.request_id = parsed_params['id']
        
        call_params = parsed_params.get('params', {})
        if isinstance(call_params, list):
            call_params = call_params[0]
        
        return (parsed_params['method'], (), call_params)    
    
    def dumps(self, result):
        
        result_dict = {
           "jsonrpc": "2.0",
           "id": self.request_id,
        }
        
        if isinstance(result, JsonRPCError):
            
            result_dict.update({
               "error": {"code": result.code,
                         "message": result.message}
            })
        else:
            result_dict.update({
                "result": result,
            })
        
        return json.dumps(result_dict)
