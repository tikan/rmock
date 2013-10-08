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

import requests
import logging
import time

from nose.tools import assert_equals
from nose.tools import assert_true
from nose.tools import assert_is
from nose.tools import assert_in
from nose.tools import assert_raises
from nose.tools import assert_raises_regexp

import rmock

from rmock import call
from rmock.errors import RmockError
from rmock.tools import find_random_port
from testtools import http_call

class TestRmockStartStopServer(object):
        
    def test_server_already_running(self):
        port = find_random_port()
        
        with rmock.run(port=port):
        
            assert_raises_regexp(
                RmockError,
                'error starting server process.*port.*%s.*' % port,
                rmock.run,
                port=port
            )
    
    # def test_stop_server(self):
    #     port = find_random_port()
    #
    #     with rmock.run(port=port) as mock:
    #         assert_equals(http_call(mock, "func").text, '')
    #         mock.stop_server()
    #
    #         # to prevent connection reset by peer socket error
    #         #time.sleep(.1)
    #         assert_raises((requests.ConnectionError),
    #                       http_call,
    #                       mock,
    #                       'func')
    #
    #         mock.start_server()
    #         assert_equals(http_call(mock, "func").text, '')

@rmock.patch("http", classvar="http_mock")
class TestRmockStartStopServerClassDecorator(object):
    """
    While patch as using class decorator mock server should be started
    and ready to handle requests always, event if it was stopped in previous test execution
    """
    def test_function1(self):
        assert_equals(http_call(self.http_mock, "func").text, '')
        self.http_mock.stop_server()
    
    def test_function2(self):
        assert_equals(http_call(self.http_mock, "func").text, '')
        self.http_mock.stop_server()
