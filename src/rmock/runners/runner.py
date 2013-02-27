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

import sys
import logging

logger = logging.getLogger("rmock.runner")

class RmockRunner(object):
      
    def __init__(self):
        self.run_params = {}
        
    def run(self, rmock_data):
        raise NotImplementedError()
    
    def handle_signal(self, sig, *args):
        logger.info("stopping; killed by signal %s", sig)
        sys.exit(0)
