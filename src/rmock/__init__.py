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

import rmock.core
import rmock.sideeffect

from rmock.core import Rmock
from rmock.core import RmockRunManager

from rmock.errors import RmockError

import copy_reg
import types

def _reduce_method(m):
    return (getattr, (m.__self__, m.__func__.__name__))

copy_reg.pickle(types.MethodType, _reduce_method)

_run_manager = RmockRunManager()

run = _run_manager.run
create = _run_manager.create
get = _run_manager.get
patch = _run_manager.patch
enable_logging = _run_manager.enable_logging
get_logger = _run_manager.get_logger 
create_remote = _run_manager.create_remote
register_remote = _run_manager.register_remote
configure = rmock._run_manager.configure

call = rmock.core.call
call_subset = rmock.core.call_subset
params_subset = rmock.core.params_subset
timeout_side_effect = rmock.sideeffect.timeout_side_effect
Spec = rmock.core.Spec
