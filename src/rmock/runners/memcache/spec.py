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

import rmock
import rmock.core
from rmock.core import Spec

from rmock import register_remote
from rmock import create_remote

logger = logging.getLogger("rmock.memcache")

class _MemcacheImpl(object):

    def __init__(self):
        self.cache = {}

    def set(self, key, value, **kwargs):
        logger.debug("memcache-impl: set %s %s", key, value)
        self.cache[key] = value
        return True

    def get(self, key):
        logger.debug("memcache-impl: get %s", key)
        return self.cache.get(key)
    
    def delete(self, key):
        logger.debug("memcache-impl: delete %s", key)
        return self.cache.pop(key, 0)
    
    def add_to_cache(self, key, value):
        self.cache[key] = value
    
    def clear(self):
        self.cache = {}

register_remote(_MemcacheImpl)

class MemcacheSpec(Spec):
    
    def __init__(self, cache=None):
        Spec.__init__(self)
        self._start_cache = cache or {}
        
        self.memcache_impl = None
    
    def apply(self, mock):
        
        self._create_memcache_impl()
        
        mock.get.side_effect = self.memcache_impl.get
        mock.set.side_effect = self.memcache_impl.set
        mock.delete.side_effect = self.memcache_impl.delete
    
    def _create_memcache_impl(self):
        
        if self.memcache_impl is None:
            self.memcache_impl = create_remote(_MemcacheImpl)
        
            for key, value in self._start_cache.iteritems():
                self.memcache_impl.add_to_cache(key, value)
    
    def add_value(self, key, value):
        self.memcache_impl.add_to_cache(key, value)
    
    def reset(self):
        
        if self.memcache_impl:
            self.memcache_impl.clear()
