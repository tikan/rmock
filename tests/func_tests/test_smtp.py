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

import _pythonpath

import socket

from nose.tools import assert_equals
from nose.tools import assert_raises

from smtplib import SMTPHeloError
from smtplib import SMTPResponseException
from smtplib import SMTPDataError

from testtools import smtp_call

import time

import rmock

from rmock.comparators import any_of
from rmock.comparators import is_
from rmock.tools import find_random_port
from rmock import call

def rcpt_to(rcpt):
    if rcpt == 'openapi@onet.pl':
        return '250 OK'
    else:
        return '500 ERROR'

class TestSmtp(object):
    
    PORT = find_random_port()

    # local_hostname which is used in smtp_call helper
    helo_name = socket.gethostname()

    def setup(self):
        self.mock = rmock.run("smtp",
                              port=self.PORT)
    
    def test_simple_email(self):
        
        smtp_call(self.mock,
                  'openapi@onet.pl',
                   ['openapi@onet.pl'],
                   'mail mail mail')
        
        self.mock.helo.assert_called_with(self.helo_name)
        self.mock.mail_from.assert_called_with('openapi@onet.pl')
        self.mock.rcpt_to.assert_called_with('openapi@onet.pl')
        self.mock.data.assert_called_with('mail mail mail')
    
    def test_email_with_return_values(self):
                
        data_result = "data data data"
        self.mock.data.return_value = '250 %s' % data_result
        
        result = smtp_call(self.mock,'openapi@onet.pl',
                             ['openapi@onet.pl'],
                             'mail mail mail')
        
        assert_equals(result['senderrs'], {})
        assert_equals(result['data_resp'], data_result)
    
    def test_email_with_rcpt_errors(self):
        
        self.mock.rcpt_to.side_effect = rcpt_to
        self.mock.data.return_value = '250 ok'
        
        result = smtp_call(self.mock, 'openapi@onet.pl',
                             ['openapi@onet.pl',
                              'alamakota@op.pl'],
                             'mail mail mail',
                             with_quit=True)
        
        
        assert_equals(result['senderrs'], {'alamakota@op.pl': (500, 'ERROR')})
        assert_equals(result['data_resp'], 'ok')
        
        self.mock.mail_from.assert_called_with('openapi@onet.pl')
        self.mock.rcpt_to.assert_called_with('openapi@onet.pl')
        self.mock.rcpt_to.assert_called_with('alamakota@op.pl')
        self.mock.data.assert_called_with('mail mail mail')
        self.mock.quit.assert_called_with()
    
    def test_email_with_helo_errors(self):
        self.mock.helo.return_value = '499 no good'
                
        assert_raises(SMTPHeloError,
                      smtp_call, self.mock, 'openapi@onet.pl',
                            ['openapi@onet.pl'],
                             'mail mail mail')
    
    def test_email_with_mail_from_errors(self):
        self.mock.mail_from.return_value = '502 no good'
        
        assert_raises(SMTPResponseException,
                      smtp_call, self.mock, 'openapi@onet.pl',
                            ['openapi@onet.pl'],
                             'mail mail mail')
    
    def test_email_with_data_errors(self):
        self.mock.data.return_value = '404 not found'
        
        assert_raises(SMTPDataError,
                      smtp_call, self.mock, 'openapi@onet.pl',
                            ['openapi@onet.pl'],
                             'mail mail mail')
    
    def teardown(self):
        self.mock.finalize()

@rmock.patch("smtp",
             whole_session=True,
             classvar="smtp_mock")
class TestSmtpWholeSession(object):

    # local_hostname which is used in smtp_call helper
    helo_name = socket.gethostname()
 
    def test_whole_session_simple_email(self):
        smtp_call(self.smtp_mock,
                  'openapi@onet.pl',
                   ['openapi@onet.pl'],
                   'mail mail mail')
        
        self.smtp_mock.sendmail.assert_called_with(
            helo=self.helo_name,
            mail_from='openapi@onet.pl',
            rcpt_to=['openapi@onet.pl'],
            data='mail mail mail'
        )
                
    def test_whole_session_multiple_calls(self):
        smtp_call(self.smtp_mock,
                  'openapi@onet.pl',
                   ['kchmiel@spoko.pl', 'pwidget@onet.eu'],
                   'mail2 mail2 mail2')
        
        smtp_call(self.smtp_mock,
                  'openapi22@onet.pl',
                   ['kchmiel@spoko.pl', 'pwidget@onet.eu', 'aaa@bbbccc.pl'],
                   'mail4 mail8 mail16')
        
        self.smtp_mock.sendmail.assert_has_calls([
            call(
                 helo=self.helo_name,
                 mail_from='openapi@onet.pl',
                 rcpt_to=['kchmiel@spoko.pl', 'pwidget@onet.eu'],
                 data='mail2 mail2 mail2'
            ),
            call(
                 helo=self.helo_name,
                 mail_from='openapi22@onet.pl',
                 rcpt_to=['kchmiel@spoko.pl', 'pwidget@onet.eu', 'aaa@bbbccc.pl'],
                 data='mail4 mail8 mail16'
            )                                    
        ])
        
    def test_whole_session_error(self):
        
        self.smtp_mock.sendmail.return_value = '500 data error'
        
        assert_raises(SMTPDataError,
                      smtp_call, self.smtp_mock, 'openapi@onet.pl',
                            ['openapi@onet.pl'],
                             'mail mail mail')
        
        self.smtp_mock.sendmail.assert_called_with(
            helo=self.helo_name,
            mail_from='openapi@onet.pl',
            rcpt_to=['openapi@onet.pl'],
            data='mail mail mail'
        )
