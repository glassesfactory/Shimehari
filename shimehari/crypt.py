#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
===============================
    Shimehari.crypt
    ~~~~~~~~~~~~~~~~~
    セキュアアアア
===============================
"""

import uuid
from hashlib import sha1
import datetime
import time
import hmac

from werkzeug.exceptions import abort
from werkzeug.routing import NotFound

from shimehari import session, shared, request
from shimehari.configuration import ConfigManager


"""
https://github.com/sjl/flask-csrf
"""


_exemptions = []


def csrfExempt(action):
    _exemptions.append(action)
    return action


class CSRF(object):

    def __init__(self, app, csrfHandler=None):
        self.app = app
        self.csrfHandler = csrfHandler

    def checkCSRFExempt(self):
        try:
            dest = self.app.controllers.get(request.endpoint)
            shared._csrfExempt = dest in _exemptions
        except NotFound:
            shared._csrfExempt = False

    #token の有効期限チェック
    def checkCSRFExpire(self, token):
        csrfCreateAt = session.get('_csrfTokenAdded', None)
        expire = self.app.config.get('CSRF_EXPIRE', None)
        if expire is None:
            return True
        now = datetime.datetime.now()
        currentTime = time.mktime(now.timetuple())
        term = currentTime - csrfCreateAt
        if term > expire:
            return False
        return True

    def csrfProtect(self):
        if shared._csrfExempt:
            return

        if not request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return

        token = session.get('_csrfToken', None)
        if not token:
            # CSRF token missing
            abort(403)

        config = ConfigManager.getConfig()
        secretKey = config['SECRET_KEY']

        hmacCompare = hmac.new(secretKey, str(token).encode('utf-8'), digestmod=sha1)

        if hmacCompare.hexdigest() != request.form.get('_csrfToken'):
            # invalid CSRF token
            if self.csrfHandler:
                self.csrfHandler(*self.app.matchRequest())
            else:
                abort(403)

        if not self.checkCSRFExpire(token):
            # CSRF token expired
            abort(403)


def generateCSRFToken():
    if not '_csrfToken' in session:
        session['_csrfToken'] = genereateToken()

    now = datetime.datetime.now() + datetime.timedelta()
    session['_csrfTokenAdded'] = time.mktime(now.timetuple())

    config = ConfigManager.getConfig()
    secretKey = config['SECRET_KEY']

    hmacCsrf = hmac.new(secretKey, str(session['_csrfToken']).encode('utf-8'), digestmod=sha1)
    return hmacCsrf.hexdigest()


import string
import random


def genereateToken():
    def randstr(n):
        return ''.join(random.choice(string.digits + string.letters) for i in xrange(n))
    token = sha1(session.sid + randstr(6)).hexdigest()
    token = uuid.uuid5(uuid.NAMESPACE_URL, token)
    return token
