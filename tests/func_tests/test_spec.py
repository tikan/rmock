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

from nose.tools import assert_equals
from nose.tools import assert_raises

from testtools import http_call
from testtools import memcache_call
from testtools import smtp_call

import rmock
from rmock.tools import find_random_port
from smtplib import SMTPDataError

class ResultsSpec(rmock.Spec):
    
    def __init__(self, **kwargs):
        rmock.Spec.__init__(self)
        self.results = kwargs
    
    def apply(self, mock):
        
        for func, value in self.results.iteritems():
            getattr(mock, func).return_value = value
    
class TestRmockSpec(object):
    
    def test_http_spec_simple(self):
        
        spec = ResultsSpec(function1='result1',
                           function2='result2')
        
        with rmock.run(
            "http",
            port=find_random_port(),
            spec=spec
        ) as mock:    
            assert_equals(http_call(mock, 'function1').text, 'result1')
            assert_equals(http_call(mock, 'function2').text, 'result2')
            assert_equals(http_call(mock, 'function3').text, '')

    def test_spec_autospec_http(self):
        
        http_spec = ResultsSpec(function1='result1',
                                function2='result2')  
        
        with rmock.run(
            "http",
            port=find_random_port(),
            spec=http_spec,
            autospec=True
        ) as mock:    
            assert_equals(http_call(mock, 'function1').text, 'result1')
            assert_equals(http_call(mock, 'function2').text, 'result2')
            assert_equals(http_call(mock, 'function3').code, 404)
        
    def test_spec_autospec_memcache(self):
        memcache_spec = ResultsSpec(get='getresult')
                
        with rmock.run(
            "memcache",
            port=find_random_port(),
            spec=memcache_spec,
            autospec=True
        ) as mock:
            assert_equals(memcache_call(mock, 'get', 'a'), 'getresult')    
            assert_equals(memcache_call(mock, 'set', 'a', 'b'), 0)
        
    def test_spec_autospec_smtp(self):
        
        smtp_spec = ResultsSpec(
            helo='250 OK',
            mail_from='250 OK',
            rcpt_to='250 OK'
            # data not allowed
        )
        with rmock.run(
            "smtp",
            port=find_random_port(),
            spec=smtp_spec,
            autospec=True
        ) as mock:
            assert_raises(
                SMTPDataError,
                smtp_call,
                mock,
                'ala@makota.pl',
                'ala@makota.pl',
                'mail'                
            )
