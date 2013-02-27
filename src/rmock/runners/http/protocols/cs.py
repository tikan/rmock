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
import urlparse

import phpserialize
from rmock.errors import RmockError

logger = logging.getLogger("rmock.cs")

class CsProtocol(object):
    
    # TODO: better error handling
    
    def __init__(self, *args, **kwargs):
        self.main_key = None
    
    def loads(self, method, url, body):
        '''        
        returns (args, kwargs)
        '''
        
        '''data': params, 
                'system': {
                    'cmd': method_name
                }
            }'''
                
        parsed_url = urlparse.urlparse(url)
        req_body = parsed_url.query if method == 'get' else body
        
        parsed_params = urlparse.parse_qsl(req_body)
        parsed_params = phpserialize.loads(parsed_params[0][1])
        
        keys = parsed_params.keys()
        
        if len(keys) > 1:
            raise RmockError("cs multicalls not supported")
        
        self.main_key = keys[0]
        req_params = parsed_params[self.main_key]
        
        return (req_params['system']['cmd'], (), req_params['data'])
    
    def dumps(self, result):
        
        result_dict = {self.main_key: {'system': {'status': 'OK'},
                                       'data': result}}

        
        return 'vars=' + phpserialize.dumps(result_dict)
