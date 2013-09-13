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

import copy
import logging

from rmock import config

logger = logging.getLogger("rmock.tools")

def len_trim(s, max_len=100):
    """Trim given string to given length, adding ... if needed"""
    if len(s) <= max_len:
        return s
    
    return s[:max_len - 3] + '...'

def dict_apply(dct, callback, make_copy=True):
    """
    `map` equivalent for dict values

    :param dct: mapping
    :param callback: one argument function which is applied to each value of mapping
    :param make_copy: if it's True then deep copy of mapping is created and returned; if
        it's False then mapping is modified inplace and then returned
    :return: original, modified dictionary or deep copy of it, depending on `make_copy` parameter value
    """
    elem = copy.deepcopy(dct) if make_copy else dct
    return _dict_apply_impl(elem, callback)

def _dict_apply_impl(elem, callback):
    if isinstance(elem, dict):
        for key in elem:
            elem[key] = dict_apply(elem[key], callback)
    elif isinstance(elem, list):
        for i, x in enumerate(elem):
            elem[i] = dict_apply(x, callback)
    elif isinstance(elem, tuple):
        return tuple(dict_apply(list(elem), callback))
    else:
        elem = callback(elem)
    
    return elem

def len_trim_dict(dct, max_len=None):
    """
    Apply `len_trim` to all mapping values

    :param max_len: `max_len` argument to `len_trim`; if not specified then
        value from rmock configuration is used
    """
    if max_len is None:
        max_len = config.get_config()['trim_len']
    
    return dict_apply(dct,
        lambda x: len_trim(x, max_len) if isinstance(x, basestring) else x
    )

def dict_contains(dcta, dctb):
    """
    Check whether first mapping is subset of second mapping
    
    Mapping A as is defined to be subset of mapping B if for all keys in A values in B are the same as in A.
    """
    return all(key in dctb and dcta[key] == dctb[key] for key in dcta)

class attr_dict(dict):

    """Mapping which allows attribute-like access to its keys"""

    def __setattr__(self, item, value):
        self[item] = value
    
    def __getattr__(self, item):
        return self[item]
