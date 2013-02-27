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

from rmock.runners.smtp.server import SMTPServerEngine
from rmock.runners.smtp.server import SMTPServer

class LMTPServerEngine(SMTPServerEngine):
    HELO_COMMANDS = ('LHLO',)

class LMTPServer(SMTPServer):
    ENGINE_CLS = LMTPServerEngine
