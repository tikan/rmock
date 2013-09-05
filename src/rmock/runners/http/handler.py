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

from tornado.web import RequestHandler 
from tornado.web import HTTPError

from rmock.runners.http.protocols import RawProtocol
from rmock.runners.http.protocols.jsonrpc import JsonRPCError

from rmock.tools import len_trim
from rmock.tools import len_trim_dict
from rmock.errors import InvalidFunction

logger = logging.getLogger("rmock.http")

def with_exception_handling(func):

    def inner(*args, **kwargs):

        try:
            return func(*args, **kwargs)
        except (HTTPError, JsonRPCError) as e:
            logger.info("error result: %s", e)
            raise
        except InvalidFunction as e:
            #invalid function call
            raise HTTPError(404)
        except Exception:
            logger.exception("unexpected error")
            raise HTTPError(500)
    
    return inner

class HttpResult(object):
    def __init__(self, code=200, body=None, headers=None):
        self.code = code
        self.headers = headers
        self.body = body

# new code should use HttpResult instead of HttpCode
# HttpCode will me marked as deprecated in the near future
HttpCode = HttpCodeError = HttpResult

class MockHttpHandler(RequestHandler):
    
    @with_exception_handling
    def initialize(self,
                   rmock_data,
                   protocol_class,
                   protocol_args,
                   slug):
        
        self.rmock_data = rmock_data
        self.slug = slug        
        
        protocol_args = protocol_args or {}        
        
        #TODO: handle in more generic way
        if protocol_class == RawProtocol:
            protocol_args.update(slug=slug)
        
        self.protocol = protocol_class(**protocol_args)
    
    @with_exception_handling
    def process_http_method(self):
                
        funcname, args, kwargs = self.protocol.loads(
            self.request.method.lower(),
            self.request.uri,
            self.request.body
        )
        
        result = self._process_function_call(funcname, args, kwargs)        
        result = self.protocol.dumps(result)
        self._write_result(result)
    
    get = process_http_method    
    post = process_http_method

    def _write_result(self, result):
        logger.debug("call result: %s", result)
        
        if result is not None and not isinstance(result, basestring):
            result = str(result)
        
        self.write(result or '')
    
    def _process_function_call(self, funcname, args, kwargs):
        
        headers = dict(self.request.headers)
        
        logger.info("call: funcname=%s args=%s kwargs=%s", 
            len_trim(funcname),
            len_trim_dict(list(args)),
            len_trim_dict(kwargs)
        )
        
        logger.debug("call: headers=%s", headers)
        
        result = self._process_function_call_impl(
            funcname, args, kwargs, headers
        )
        
        result = self._transform_result(result)

        logger.debug("result: %s", result)
        
        return result

    def _transform_result(self, result):
        if isinstance(result, HttpResult):
            if result.code != 200:
                raise HTTPError(result.code)
            if result.headers is not None:
                for header, value in result.headers:
                    self.set_header(header, value)

            result = result.body

        return result

    def _process_function_call_impl(self, funcname, args, kwargs, headers):
        return self.rmock_data.register_call_and_get_result(
            funcname, args, kwargs,
            headers=headers
        )
