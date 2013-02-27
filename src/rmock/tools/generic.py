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

    if len(s) <= max_len:
        return s
    
    return s[:max_len - 3] + '...'

def dict_apply(dct, callback, make_copy=True):
    
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
    
    def __setattr__(self, item, value):
        self[item] = value
    
    def __getattr__(self, item):
        return self[item]
