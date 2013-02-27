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
#under the License.
#

import logging

from .server import SMTPServer

from rmock.runners.runner import RmockRunner

from rmock.tools import len_trim
from rmock.tools import len_trim_dict
from rmock.errors import InvalidFunction
from rmock.tools.net import find_port

logger = logging.getLogger("rmock.smtp")

class SimpleMockSmtpHandler(object):
    """
    Mock implementation of smtp handler
    """
    
    def __init__(self, rmock_data):
        self.rmock_data = rmock_data
        
    def helo(self, helo_name):
        return self._process_call("helo", (helo_name,))
    
    def mailFrom(self, from_):
        return self._process_call("mail_from", (from_,))
        
    def rcptTo(self, rcpt):
        return self._process_call("rcpt_to", (rcpt,))

    def data(self, data_):
        return self._process_call("data", (data_,))

    def quit(self, args):
        return self._process_call("quit", ())
    
    def reset(self, args):
        return self._process_call("reset", args)
    
    def _process_call(self, function, args, kwargs=None):
        
        logger.info("call: funcname=%s args=%s kwargs=%s", 
            len_trim(function),
            len_trim_dict(list(args)),
            len_trim_dict(kwargs or {})
        )
        
        try:
            result = self.rmock_data.register_call_and_get_result(function, args, kwargs or {})
        except InvalidFunction:
            result = '502 command not implemented'
        except Exception:
            logger.exception("exception occured")
            result = '504 internal error'
        
        logger.debug("%s result: %s", function, result)
        return result

class WholeSessionSmtpHandler(SimpleMockSmtpHandler):
    
    def __init__(self, rmock_data):
        SimpleMockSmtpHandler.__init__(self, rmock_data)
        
        self._reset_calls()
    
    def helo(self, helo_name):
        #todo: rmock_data.get_result(...)
        
        self._helo = helo_name
    
    def mailFrom(self, from_):
        self._mail_from = from_
        
    def rcptTo(self, rcpt):
        self._rcpt_to.append(rcpt)

    def data(self, data_):
        result = self._process_call(
            "sendmail",
            args=(), kwargs=dict(
                helo=self._helo,
                mail_from=self._mail_from,
                rcpt_to=self._rcpt_to,
                data=data_)
        )
        
        self._reset_calls()
        
        return result

    def quit(self, args):
        self._reset_calls()
    
    def reset(self, args):
        pass
    
    def _reset_calls(self):
        
        #helo is spefified only once during smtp session, so we should not clear it
        #self._helo = None
        self._mail_from = None
        self._rcpt_to = []

class SmtpRunner(RmockRunner):
    
    SERVER_CLS = SMTPServer
    
    def __init__(self, port=None, whole_session=False):
        RmockRunner.__init__(self)
        
        # random port support
        port = find_port(port)
        self.port = port
        self.whole_session = whole_session
        
        self.run_params.update(port=port)
    
    def run(self, rmock_data):
        
        logger.info("smtp server start; listening on port=%s", self.port)
        handler_cls = WholeSessionSmtpHandler if self.whole_session else SimpleMockSmtpHandler    
        server_impl = handler_cls(rmock_data)
        server = self.SERVER_CLS(self.port)
        server.serve(server_impl)
    
    def __str__(self):
        return "smtp(port=%s)" % self.port
