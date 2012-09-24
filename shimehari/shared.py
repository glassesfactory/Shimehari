#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
===============================
    Shimehari.shared
    ~~~~~~~~~~~~~~~~
    アプリケーション内で共通して使いたい物たち

===============================
"""
from functools import partial
from werkzeug.local import LocalProxy, LocalStack


class _SharedRequestClass(object):
    pass


def _lookUpObjectInRequestContext(name):
    top = _requestContextStack.top
    if top is None:
        raise RuntimeError('ahixi...')
    return getattr(top, name)


def findApp():
    top = _appContextStack.top
    if top is None:
        raise RuntimeError('AppContext is none...')
    return top.app


_requestContextStack = LocalStack()
_appContextStack = LocalStack()
currentApp = LocalProxy(findApp)
request = LocalProxy(partial(_lookUpObjectInRequestContext, 'request'))
session = LocalProxy(partial(_lookUpObjectInRequestContext, 'session'))
shared = LocalProxy(partial(_lookUpObjectInRequestContext, 'shared'))
