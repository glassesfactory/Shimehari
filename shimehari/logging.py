# -*- coding: utf-8 -*-
#!/usr/bin/env python

u"""
===============================
    Shimehari.logging
    ~~~~~~~~~~~~~~~~~
    ロガー
    Flask などなど参考に。
    ルーティングが多少複雑になっても
    対応できるような作りにしたいなぁ
===============================
"""

from __future__ import absolute_import

from logging import getLogger, StreamHandler, Formatter, getLoggerClass, DEBUG

def createLogger(app):

    Logger = getLoggerClass()

    class DebugLogger(Logger):
        def getEffectiveLevel(x):
            if x.level == 0 and app.debug:
                return DEBUG
            return Logger.getEffectiveLevel(x)

    class DebugHandler(StreamHandler):
        def emit(x,record):
            StreamHandler.emit(x,record) if app.debug else None

    handler = DebugHandler()
    handler.setLevel(DEBUG)
    handler.setFormatter(Formatter(app.debugLogFormat))
    logger = getLogger(app.loggerName)

    del logger.handlers[:]
    logger.__class__ = DebugLogger
    logger.addHandler(handler)
    return logger