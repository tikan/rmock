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

import rmock
from rmock.tools import find_random_port

import rmock.tools.net
from rmock.tools.net import find_port
from rmock.tools.net import RANDOM_PORT

from rmock.errors import RmockError

import mock

from nose.tools import assert_raises
from nose.tools import assert_equals

def test_find_random_port_ok():
    
    port = find_random_port()
        
    with rmock.run(port=port):
        pass

def test_find_random_port_fail():
     
    port = find_random_port()

    with mock.patch("random.randint") as randint:
            
        randint.return_value = port
        with rmock.run(port=port):        
            assert_raises(RmockError, find_random_port)

def test_find_port():
    assert_equals(find_port(10), 10)
    
    port = find_random_port()  
    
    with mock.patch("random.randint") as randint:
        randint.return_value = port
        
        assert_equals(find_port(RANDOM_PORT), port)
        assert_equals(find_port('random'), port)
        assert_equals(find_port('RANDOM'), port)
