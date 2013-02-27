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

import urlparse
import logging

from rmock.errors import RmockError

logger = logging.getLogger("rmock.raw")

class RawProtocol(object):
    
    name = 'raw'
    url_sub_re = re.compile(r'/+')
    
    def __init__(self,
                 parse_url_params=False,
                 parse_post_body=False,
                 params_parser=None,
                 slug=None):
        
        self.parse_url_params = parse_url_params
        self.parse_post_body = parse_post_body
        self.params_parser = params_parser
        self.slug = slug
        
    def loads(self, method, url, body):
        
        url = self.url_sub_re.sub('/', url)
        parsed_url = urlparse.urlparse(url)
        
        params_parser = self.params_parser or self._get_funcname_arguments
            
        funcname, args, kwargs = params_parser(method, parsed_url, body)
        return funcname, args, kwargs
    
    def dumps(self, result):
        return result
    
#    def dumps_error(self, status, data):
#        return self._serialize_dict({}, status=status)
    
    def _get_funcname(self, parsed_url):
        
        funcname = parsed_url.path.strip('/')
                
        if self.slug:
            funcname = funcname[len(self.slug):]
            funcname = funcname.strip('/')
        
        if self.parse_url_params:
            funcname, _, suffix = funcname.partition('/') 
        else:
            funcname, suffix = funcname.replace('/', '_'), ''
        
        return funcname, suffix
    
    def _get_funcname_arguments(self, method, parsed_url, body):
        
        if method not in ('get', 'post'):
            raise RmockError("unsupported http method: %s" % self.request.method)
         
        funcname, suffix = self._get_funcname(parsed_url)
        args, kwargs = (), {}
        
        if self.parse_url_params and suffix:
            args += (suffix,)        
        
        if method == 'get':
            kwargs = self._format_arguments(urlparse.parse_qs(parsed_url.query))
        elif method == 'post':
            
            if self.parse_post_body:
                kwargs.update(self._format_arguments(urlparse.parse_qs(body)))            
            else:
                args += (body, )
                
                if parsed_url.query:
                    kwargs = self._format_arguments(urlparse.parse_qs(parsed_url.query))
        
        return funcname, args, kwargs
    
    def _format_arguments(self, dct):
        return {name: values if len(values) >= 2 else values[0]
                for (name, values) in dct.iteritems()}
