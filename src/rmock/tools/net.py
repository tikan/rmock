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

import random
import socket

from rmock.errors import RmockError
from rmock import config

RANDOM_PORT_RANGE_START = 1024
RANDOM_PORT_RANGE_END = 65535

def find_random_port(tries=None):
    
    if tries is None:
        tries = config.get_config()['random_port_tries']    
    
    while tries:
        port = random.randint(RANDOM_PORT_RANGE_START, RANDOM_PORT_RANGE_END)
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('', port))
        except socket.error:
            pass
        else:
            return port
        
        tries -= 1
    
    raise RmockError("error finding random port; tries number exceeded")

class RANDOM_PORT(object):
    pass

def find_port(port):
    if port in (0, None, RANDOM_PORT, 'random', 'RANDOM'):
        return find_random_port()
    
    return port
