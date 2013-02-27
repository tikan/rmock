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

from nose.tools import assert_equals
from nose.tools import assert_true

import rmock
from rmock.comparators import any_

from testtools import lmtp_call

class TestLmtp(object):
    
    mail_from = 'email@email.com'
    rcpt_to = 'email-to@email.com'
    mail_body = 'e mail body'    
    
    def test_lmtp_simple(self):
        with rmock.patch("lmtp") as mock:
                        
            lmtp_call(mock, self.mail_from, [self.rcpt_to],
                      self.mail_body)
            
            mock.helo.assert_called()
            mock.mail_from.assert_called_with(self.mail_from)
            mock.rcpt_to.assert_called_with(self.rcpt_to)
            mock.data.assert_called_with(self.mail_body)
            
    def test_lmtp_whole_session(self):
        with rmock.patch("lmtp", whole_session=True) as mock:
            
            lmtp_call(mock, self.mail_from, [self.rcpt_to],
                      self.mail_body)
            
            mock.sendmail.assert_called_with(helo=any_(),
                                             mail_from=self.mail_from,
                                             rcpt_to=[self.rcpt_to],
                                             data=self.mail_body)
