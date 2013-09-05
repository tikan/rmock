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

import _pythonpath

from urllib2 import urlopen
from urllib2 import HTTPError

from nose.tools import assert_raises
from nose.tools import assert_equals
from nose.tools import assert_in

import rmock

from rmock.errors import RmockParamsError

from rmock.runners.http import HttpCode
from rmock.runners.http import HttpResult
from rmock.tools.net import find_random_port
from testtools import http_call

rmock.configure(trim_len=1000)

class TestHttp(object):
    
    @classmethod
    def setup_class(cls):
        
        cls.port = find_random_port()
        cls.mock = rmock.run('http',
                             port=cls.port)
    
    def setup(self):
        self.mock.reset()
    
    def test_http_simple_get(self):
        
        http_call(self.mock, 'funcc1', a=10, b=20, c=30)
        http_call(self.mock, 'funcc2')
        http_call(self.mock, 'funcc3', asdsadsad=12321321321)
        
        self.mock.funcc1.assert_called_with(a='10', b='20', c='30')
        self.mock.funcc2.assert_called_with()
        self.mock.funcc3.assert_called_with(asdsadsad='12321321321')
            
    def test_http_simple_post(self):
        
        urlopen('http://localhost:%s/funcc1?a=10&b=20&c=30' % self.port,
                'bodybody')
        
        self.mock.funcc1.assert_called_with('bodybody',
                                            a='10', b='20', c='30')        
    
    def test_http_with_slashes(self):
        
        http_call(self.mock, 'admin/mail', a=10, b=20, c=30)
        
        self.mock.admin_mail.assert_called_with(a='10', b='20', c='30')
        self.mock.admin_mail.assert_called_once_with(a='10', b='20', c='30')
    
    def test_http_results_simple(self):
        self.mock.func.return_value = '213'
        
        assert_equals(
            http_call(self.mock, 'func').text,
            '213'
        )
        
        assert_equals(
            http_call(self.mock, 'func', a=10).text,
            '213'
        )
        
        assert_equals(
            http_call(self.mock, 'func2', a=10).text,
            ''
        )
    
    def test_http_results_with_args(self):
        
        self.mock.func.return_value = 'generic'
        self.mock.func().return_value = 'no args'
        self.mock.func(a='10').return_value = 'one arg'
                
        assert_equals(
            http_call(self.mock, 'func').text,
            'no args'
        )
        
        assert_equals(
            http_call(self.mock, 'func', a='10').text,
            'one arg'
        )
        
        assert_equals(
            http_call(self.mock, 'func', a=10, b=20).text,
            'generic'
        )
        
        assert_equals(
            http_call(self.mock, 'func', a=10, b=20).text,
            'generic'
        )
        
        with assert_raises(AssertionError) as ctx:
            self.mock.func.assert_called_once_with(a='10', b='20')
        
        assert_in("func called 4 times (1 expected)", str(ctx.exception))
            
    def test_http_invalid_port(self):
        assert_raises(rmock.RmockError,
                      rmock.run, port=-1)
    
    def test_http_error_code_get(self):
        self.mock.func.return_value = HttpCode(500)
                
        assert_equals(http_call(self.mock, 'func').code,
                      500)
    
    def test_http_error_code_post(self):
        self.mock.func.return_value = HttpCode(500)
                
        with assert_raises(HTTPError) as raises_ctx:
            urlopen('http://localhost:%s/func' % self.port, '')
        
        assert_equals(raises_ctx.exception.code, 500)
    
    def test_http_with_slug(self):
        
        current_port = find_random_port()
        slug_mock = rmock.run(port=current_port,
                                    slug='slug')
        
        slug_mock.func.return_value = '321'
        slug_mock.func2(b='b').return_value = '123'
        
        assert_equals(
            http_call(slug_mock, 'func', z=17).text,
            '321'
        )
        
        assert_equals(
            http_call(slug_mock, 'func').text,
            '321'
        )
        
        assert_equals(
            http_call(slug_mock, 'func2', b='b').text,
            '123'
        )
                
        with assert_raises(HTTPError) as raises_ctx:
            urlopen('http://localhost:%s/zzzslugzzz/func2?b=b' % current_port)
        
        assert_equals(raises_ctx.exception.code, 404)
        
        with assert_raises(HTTPError) as raises_ctx:
            urlopen('http://localhost:%s//slugzzz/func2?b=b' % current_port)
        
        assert_equals(raises_ctx.exception.code, 404)
    
    def test_http_with_long_slug(self):
        
        with rmock.run(port="random",
                       slug='urlprefix/raw/raw2') as slug_mock:
        
            slug_mock.func.return_value = '321'
            slug_mock.func2(b='b').return_value = '123'
                   
            http_call(slug_mock, 'func', z='17')
            
            assert_equals(
                http_call(slug_mock, 'func', z='17').text,
                '321'
            )
            
            assert_equals(
                http_call(slug_mock, 'func').text,
                '321'
            )
            
            assert_equals(
                http_call(slug_mock, 'func2', b='b').text,
                '123'
            )
    def test_http_with_posargs(self):
        
        port = find_random_port()
        
        ghost_mock = rmock.run(port=port,
                               protocol_args=dict(parse_url_params=True))
        
        urlopen('http://localhost:%s/upload/ghostnb5_prod_03/pool2/20120731/16/13/123831710_31826553.b' % port,
                'post_data')
        
        ghost_mock.upload.assert_called_with('ghostnb5_prod_03/pool2/20120731/16/13/123831710_31826553.b',
                                             'post_data')
        
        urlopen('http://localhost:%s/ghostn10_prod_04/pool2/20120612/16/19/150976475_8133614.i' % port)
        
        ghost_mock.ghostn10_prod_04.assert_called_with('pool2/20120612/16/19/150976475_8133614.i')        
    
    def test_http_with_post_body_args(self):
        
        port = find_random_port()
        with rmock.run(port=port,
                       protocol_args=dict(parse_post_body=True)) as comet_mock:
            http_call(comet_mock, 'update_snippet',
                      mid=123, kid=213, snippet='snipppet')
            
            comet_mock.update_snippet.assert_called_with(
                mid='123',
                kid='213',
                snippet='snipppet'
            )    
    
    def test_http_with_full_url_param(self):
        port1 = find_random_port()
        
        with rmock.run(url='http://localhost:%s/slugg' % port1) as http_mock:
            http_call(http_mock, 'func', mid='444')
            
            http_mock.func.assert_called_with(
                mid='444'
            )
        
        port2 = find_random_port()
        with rmock.run(url='localhost:%s' % port2) as http_mock2:
            http_call(http_mock2, 'func', mid='444')
            
            http_mock2.func.assert_called_with(
                mid='444'
            )
        
        port3 = find_random_port()    
        with rmock.run(url='localhost:%s/aaa/bbb/ccc/' % port3) as http_mock3: 
            http_call(http_mock3, 'func', mid='444')
            
            http_mock3.func.assert_called_with(
                mid='444'
            )
    
    def test_http_with_full_url_param_fail(self):
        
        assert_raises(
            RmockParamsError,
            rmock.run,
            port="random",
            url='http://localhost:6645/slugg'
        )
        
        assert_raises(
            RmockParamsError,
            rmock.run,
            slug='ss',
            url='http://localhost:6645/slugg'
        )
    
    def test_http_parse_url_params(self):
        with rmock.run(protocol_args=dict(parse_url_params=True)) as mock:
            port = mock.runner_params.port
            urlopen('http://localhost:%s/function/a/b/c?data=dtd&s=10' % port)
            mock.function.assert_called_with('a/b/c', data='dtd', s='10')
            
            urlopen('http://localhost:%s/function2?data=dtd&s=10' % port)
            mock.function2.assert_called_with(data='dtd', s='10')

    @rmock.patch("http")
    def test_http_http_result_set_code(self, mock):
        code = 411
        mock.func.return_value = HttpResult(code=code)

        result = http_call(mock, 'func')
        assert_equals(result.code, code)

    @rmock.patch("http")
    def test_http_http_result_set_body(self, mock):
        body = "response body"
        mock.func.return_value = HttpResult(body=body)

        result = http_call(mock, 'func')
        assert_equals(result.text, body)

    @rmock.patch("http")
    def test_http_set_response_headers(self, mock):

        headers = [
            ('Content-Type', 'application/json'),
            ('my-header', 'my-value')
        ]
        mock.func.return_value = HttpResult(
            headers=headers)

        result = http_call(mock, 'func')

        for header, value in headers:
            assert_equals(result.headers[header], value)

    def teardown(self):
        self.mock.reset()
    
    @classmethod
    def teardown_class(cls):
        cls.mock.finalize()
