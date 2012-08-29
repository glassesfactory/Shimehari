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
from shimehari.configuration import ConfigManager,Config

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
    if app.config['LOG_FILE_OUTPUT']:
        fn = './' + app.config['APP_DIRECTORY'] + '.log'
        if app.config['LOG_FILE_ROTATE']:
            from logging import RotateFileHandler
            handler = RotateFileHandler(fn,'a',app.config['LOG_ROTATE_MAX_BITE'], app.config['LOG_ROTATE_COUNT'])
        else:
            from logging import FileHandler
            handler = FileHandler(fn, 'a')
        handler.setFormatter(Formatter(app.outputLogFormat))
    else:
        handler = DebugHandler()
        handler.setFormatter(Formatter(app.debugLogFormat))

    handler.setLevel(DEBUG)
    logger = getLogger(app.loggerName)

    del logger.handlers[:]
    logger.__class__ = DebugLogger
    logger.addHandler(handler)
    return logger