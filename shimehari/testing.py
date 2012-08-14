#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
===============================
    Shimehari.testing
    ~~~~~~~~~~~~~~~~~
    テスト
===============================
"""

from contextlib import contextmanager
from werkzeug.test import Client, EnvironBuilder
from shimehari import _requestContextStack


def makeTestEnvironBuilder(app, path='/', baseUrl=None, *args, **kwargs):
    httpHost = app.config.get('SERVER_NAME')
    appRoot = app.config.get('APP_ROOT')
    if baseUrl is None:
        baseUrl = 'http://%s/' % (httpHost or 'localhost')
        if appRoot:
            baseUrl += appRoot.lstrip('/')
    return EnvironBuilder(path, baseUrl, *args, **kwargs)


class ShimehariClient(Client):

    preserveContext = False

    @contextmanager
    def sessionTransaction(self, *args, **kwargs):
        if self.cookieJar is None:
            raise RuntimeError('cookieeee')

        app = self.application
        environOverrides = kwargs.setdefault('environOverrides', {})
        self.cookie_jar.inject_wsgi(environOverrides)
        otherReqContext = _requestContextStack.top
        with app.testRequestContext(*args, **kwargs) as c:
            sess = app.openSession(c.request)
            if sess is None:
                raise RuntimeError('can not open session')
            _requestContextStack.push(otherReqContext)
            try:
                yield sess
            finally:
                _requestContextStack.pop()

            resp = app.responseClass()
            if not app.sessionStore.isNullSession(sess):
                app.saveSession(sess, resp)
            headers = reqp.get_wsgi_headers(c.request.environ)
            self.cookie_jar.extract_wsgi(c.request.environ, headers)

    def open(self, *args, **kwargs):
        kwargs.setdefault('environ_overrides', {}) \
            ['shimehari._preserve_context'] = self.preserveContext

        asTuple = kwargs.pop('asTuple', False)
        buffered = kwargs.pop('buffered', False)
        followRedirects = kwargs.pop('followRedirects', False)
        builder = makeTestEnvironBuilder(self.application, *args, **kwargs)

        return Client.open(self, builder,
                           as_tuple=asTuple,
                           buffered=buffered,
                           follow_redirects=followRedirects)

    def __enter__(self):
        if self.preserveContext:
            raise RuntimeError('can not nest')
        self.preserveContext = True
        return self

    def __exit__(self, excType, excValue, tb):
        self.preserveContext = False
        top = _requestContextStack.top
        if top is not None and top.preserved:
            top.pop()
