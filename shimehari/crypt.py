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

from werkzeug.exceptions import abort
from werkzeug.routing import NotFound

from shimehari import session, shared, request

_exemptions = []

"""
https://github.com/sjl/flask-csrf
"""

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
        csrfCreateAt = session.pop('_csrfTokenAdded', None)
        expire = self.app.config['CSRF_EXPIRE']
        now = datetime.datetime.now()
        currentTime = time.mktime(now.timetuple())
        term = currentTime - csrfCreateAt
        if term > expire:
            return False
        return True


    def csrfProtect(self):
        if not shared._csrfExempt:
            if request.method == 'POST':
                token = session.pop('_csrfToken', None)
                if not token or token != request.form.get('_csrfToken'):
                    if self.csrfHandler:
                        self.csrfHandler(*self.app.matchRequest())
                else:
                    if not self.checkCSRFExpire(token):
                        abort(400)



def generateCSRFToken():
    if '_csrfToken' not in session:
        session['_csrfToken'] = genereateToken()
        now = datetime.datetime.now() + datetime.timedelta()
        session['_csrfTokenAdded'] = time.mktime(now.timetuple())
    return session['_csrfToken']

import string
import random
def genereateToken():
    def randstr(n):
        return ''.join(random.choice(string.digits + string.letters) for i in xrange(n))
    token = sha1(session.sid + randstr(6)).hexdigest()
    token = uuid.uuid5(uuid.NAMESPACE_URL, token)
    return token

