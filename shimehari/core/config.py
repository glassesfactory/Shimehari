#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
===============================
    Shimehari.core.config
    ~~~~~~~~~~~~~~~~~~~~~
    shimehari core config settings
===============================
"""

from werkzeug.datastructures import ImmutableDict

u"""
    許可する RESTful アクション
"""
RESTFUL_ACTIONS = set(['index', 'show', 'edit', 'new', 'create', 'update', 'destroy'])

u"""
    許可する HTTP メソッド
"""
ALLOWED_HTTP_METHOD_NAMES = set(['get', 'post', 'put', 'delete', 'head', 'options', 'trace'])

u"""
    RESTful アクションごとに許可する HTTP メソッドの対応マップ
"""
RESTFUL_METHODS_MAP = ImmutableDict({
    'index': ['get'],
    'show': ['get', 'post'],
    'edit': ['get', 'post'],
    'new': ['get'],
    'create': ['post'],
    'update': ['put'],
    'destroy': ['delete']
})
