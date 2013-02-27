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

import requests
import memcache

import smtplib

def smtp_sendmail(self, mail_from, rcpt_to, mail,
                   helo_name='',
                   mail_options='',
                   rcpt_options='',
                   strict_rcpt_errors=True):
        
    self.ehlo_or_helo_if_needed()
    
    if isinstance(rcpt_to, basestring):
        rcpt_to = [rcpt_to]    
    
    (code, resp) = self.mail(mail_from, options=mail_options)
    if code != 250:
        self.rset()
        raise smtplib.SMTPSenderRefused(code, resp, mail_from)
    
    senderrs = {}
    for rcpt in rcpt_to:
        (code, resp) = self.rcpt(rcpt, options=rcpt_options)
        if code not in (250, 251):
            senderrs[rcpt] = (code, resp)
    
    if len(senderrs) == len(rcpt_to):
        if strict_rcpt_errors:
            self.rset()
            raise smtplib.SMTPRecipientsRefused(senderrs)
        else:
            return {'senderrs': senderrs,
                    'data_resp': None}
    
    (code, resp) = self.data(mail)
    if code != 250:
        self.rset()
        raise smtplib.SMTPDataError(code, resp)
        
    return {'senderrs': senderrs,
            'data_resp': resp}

def http_call(mock, function, headers=None, timeout=None, **params):
    runner_params = mock.runner_params
    
    url = 'http://localhost:{port}/{slug}/{function}'.format(
        function=function,
        **runner_params
    )
    
    response = requests.get(url, params=params, headers=headers, timeout=timeout)
    response.code = response.status_code    
    
    return response

def memcache_call(mock, function,
                  *args, **kwargs):
    
    url = 'localhost:{port}'.format(**mock.runner_params)
    
    timeout = kwargs.pop('timeout', 3)
        
    client = memcache.Client([url], socket_timeout=timeout, dead_retry=0)
    return getattr(client, function)(*args, **kwargs)

def memcache_get(mock, key, **kwargs):
    return memcache_call(mock, 'get', key, **kwargs)

def memcache_set(mock, key, value, time=0, **kwargs):
    return memcache_call(mock, 'set', key, value, time=time, **kwargs)

def smtp_call(mock, mail_from, rcpt_to, data, with_quit=False):
    smtp = smtplib.SMTP('localhost', mock.runner_params.port)
    
    return _smtp_call_impl(smtp, mail_from, rcpt_to, data, with_quit)

def lmtp_call(mock, mail_from, rcpt_to, data, with_quit=False):
    lmtp = smtplib.LMTP('localhost', mock.runner_params.port)
    return _smtp_call_impl(lmtp, mail_from, rcpt_to, data, with_quit)

def _smtp_call_impl(smtp, mail_from, rcpt_to, data, with_quit):
    result = smtp_sendmail(smtp, mail_from,
                           rcpt_to,
                           data)

    if with_quit:
        smtp.quit()
    
    return result

