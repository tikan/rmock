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

import poplib
from nose.tools import assert_equals
from nose.tools import assert_raises_regexp

import rmock

class TestPop3(object):
    
    @rmock.patch("pop3")
    def test_pop3_simple(self, pop3_mock):
        port = pop3_mock.runner_params.port
        mails = {'uid1': 'mail1 content',
                 'uid2': 'mail2 content',
                 'uid3': 'mail3 content'}
        
        user, password = 'username', '123qwe'
        pop3_mock.login(user, password).return_value = True
        pop3_mock.uidl.return_value = mails.keys()
        
        for uid, mail_content in mails.iteritems():
            pop3_mock.retr(uid).return_value = mail_content
        
        pop3_cli = poplib.POP3('localhost', port)
        pop3_cli.user(user)
        pop3_cli.pass_(password)
        
        uidls = pop3_cli.uidl()
        
        for nr, uid in [s.split(' ', 1) for s in uidls[1]]:
            result = pop3_cli.retr(nr)[1][0]
            assert_equals(result, mails[uid])
        
        pop3_cli.quit()
        
        pop3_mock.login.assert_called_once_with(user, password)
        pop3_mock.uidl.assert_called_once_with()
        
        for uid, mail_content in mails.iteritems():
            pop3_mock.retr.assert_called_with(uid)
        
        pop3_mock.get_welcome.assert_called_once_with()
        pop3_mock.quit.assert_called_once_with()
    
    @rmock.patch("pop3")
    def test_pop3_invalid_login(self, pop3_mock):
        port = pop3_mock.runner_params.port
        
        user, password = 'username', '123qwe'        
        
        pop3_cli = poplib.POP3('localhost', port)
        pop3_mock.login(user, password).return_value = False
        
        pop3_cli.user(user)
        
        assert_raises_regexp(poplib.error_proto,
                             'auth error',
                             pop3_cli.pass_, password)
