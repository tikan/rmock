#!/usr/bin/env python
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

from argparse import ArgumentParser
import time

import rmock
from rmock.runners.http import JsonRPCError


def make_argparser():
    parser = ArgumentParser()
    
    parser.add_argument('runner', default='http')
    parser.add_argument('-v', dest='verbose', action='store_true')
    parser.add_argument('-p', '--port',
                        dest='port',
                        type=int)
    
    parser.add_argument('-P', '--protocol',
                        dest='protocol',)
    
    return parser

if __name__ == '__main__':
    
    parser = make_argparser()
    args = parser.parse_args()
    
    level = logging.DEBUG if args.verbose else logging.INFO
    rmock.enable_logging(level=level)
    
    params = dict(port=args.port)
    
    if args.runner == 'http':
        params['protocol'] = args.protocol
    
    from rmock.runners.memcache.spec import MemcacheSpec
    params["spec"] = MemcacheSpec()
    
    mock_server = rmock.run(args.runner, **params)
    
    #TODO: yaml config
    
    mock_server.join_server()
