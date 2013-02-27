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
import time

logger = logging.getLogger("rmock.sideeffect")

class timeout_side_effect(object):
    """
    Simple callable object which invoke sleep for given time and than returns defined result
    Could be used in side_effect of rmock.
    """
    def __init__(self, seconds, real_result=None):
        self.seconds = seconds
        self.real_result = real_result
    
    def __call__(self, *args, **kwargs):
        logger.info("waiting %s seconds...", self.seconds)
        time.sleep(self.seconds)
        return self.real_result
    
    def __str__(self):
        return 'timeout_side_effect(timeout=%s, result=%s)' % (self.seconds, self.real_result)
    
    __repr__ = __str__
