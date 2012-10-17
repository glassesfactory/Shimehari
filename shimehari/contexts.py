#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
===============================
    Shimehari.contexts
    ~~~~~~~~~~~~~~~~~~
    コンテキスト周り
===============================
"""

import sys
from werkzeug.exceptions import HTTPException
from .shared import _requestContextStack, _appContextStack


u"""-----------------------------
    ::pkg:: Shimehari.contexts
    _getNecessaryAppContext
    ~~~~~~~~~~~~~~~~~~~~~~~

    スタックからアプリケーションコンテキストを取得します。

    ------------------------------"""


def _getNecessaryAppContext(app):
    top = _appContextStack.top
    if top is None or top.app != app:
        context = app.appContext()
        context.push()
        return context


u"""-----------------------------
    ::pkg:: Shimehari.contexts
    hasAppContext
    ~~~~~~~~~~~~~

    スタックにアプリケーションコンテキストが
    格納されているかどうか bool 値で返します。
    [return]
    :bool スタックにアプリケーションコンテキストが
          格納されているかどうか

    ------------------------------"""


def hasAppContext():
    return _appContextStack.top is not None


u"""-----------------------------
    ::pkg:: Shimehari.contexts
    hasRequestContext
    ~~~~~~~~~~~~~~~~~

    スタックにリクエストコンテキストが
    格納されているかどうか bool 値で返します。
    [return]
    :bool スタックにリクエストコンテキストが
          格納さているかどうか

    ------------------------------"""


def hasRequestContext():
    return _requestContextStack.top is not None


u"""
===============================
    ::pkg:: Shimehari.contexts
    AppContext
    ~~~~~~~~~~

    アプリケーションの情報を抽象化してとっておく

===============================
"""


class AppContext(object):
    def __init__(self, app):
        self.app = app
        self.adapter = app.createAdapter(None)

    u"""-----------------------------
        ::pkg:: Shimehari.contexts.AppContext
        push
        ~~~~

        現在のアプリケーションコンテキストをスタックに追加します。

    ------------------------------"""
    def push(self):
        _appContextStack.push(self)

    u"""-----------------------------
        ::pkg:: Shimehari.contexts.AppContext
        pop
        ~~~

        アプリケーションコンテキストをスタックから取り出します。

    ------------------------------"""
    def pop(self, exc=None):
        if exc is None:
            exc = sys.exc_info()[1]
        rv = _appContextStack.pop()
        assert rv is self, 'app context auau'

    def __enter__(self):
        self.push()
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.pop()


u"""
===============================
    ::pkg:: Shimehari.contexts
    RequestContext
    ~~~~~~~~~~~~~~

    リクエストオブジェクトを抽象化して保存します

===============================
"""


class RequestContext(object):
    def __init__(self, app, environ):
        self.app = app
        self.request = app.requestClass(environ)
        self.urlAdapter = app.createAdapter(self.request)
        self.flash = None
        self.session = None
        self.shared = app.sharedRequestClass()
        self.preserved = False
        self._pushedApplicationContext = None

        self.matchRequest()

    u"""-----------------------------
        ::pkg:: Shimehari.contexts.RequestContext
        matchRequest
        ~~~~~~~~~~~~

        リクエストに対してマッチするルールが存在するかチェックします

    ------------------------------"""
    def matchRequest(self):
        try:
            urlRule, self.request.viewArgs = self.urlAdapter.match(return_rule=True)
            self.request.urlRule = urlRule
        except HTTPException, e:
            self.request.routingException = e

    u"""-----------------------------
        ::pkg:: Shimehari.contexts.RequestContext
        push
        ~~~~

        現在のリクエストコンテキストをスタックに追加します。

    ------------------------------"""
    def push(self):
        top = _requestContextStack.top
        if top is not None and top.preserved:
            top.pop()

        self._pushedApplicationContext = _getNecessaryAppContext(self.app)
        _requestContextStack.push(self)

        self.session = self.app.openSession(self.request)
        if self.session is None:
            self.session = self.app.sessionStore.makeNullSession()

    u"""-----------------------------
        ::pkg:: Shimehari.contexts.RequestContext
        pop
        ~~~

        リクエストコンテキストをスタックから取り出します。

    ------------------------------"""
    def pop(self, exc=None):
        self.preserved = False

        if exc is None:
            exc = sys.exc_info()[1]
        self.app.doRequestContextTearDown(exc)
        rv = _requestContextStack.pop()

        assert rv is self, 'zibun jan'
        rv.request.environ['werkzeug.request'] = None

        if self._pushedApplicationContext:
            self._pushedApplicationContext.pop(exc)
            self._pushedApplicationContext = None

    def __enter__(self):
        self.push()
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if self.request.environ.get('shimehari._preserve_context') or (tb is not None and self.app.preserveContextOnException):
            self.preserved = True
        else:
            self.pop(exc_value)
