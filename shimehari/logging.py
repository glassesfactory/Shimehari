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

import os
import sys

from logging import getLogger, StreamHandler, Formatter, getLoggerClass, DEBUG
from shimehari.configuration import ConfigManager,Config
from shimehari.helpers import getEnviron

def createLogger(loggerName='shimehariLoagger'):

    Logger = getLoggerClass()

    class DebugLogger(Logger):
        def getEffectiveLevel(x):
            if x.level == 0 and config['DEBUG']:
                return DEBUG
            return Logger.getEffectiveLevel(x)

    class DebugHandler(StreamHandler):
        def emit(x,record):
            StreamHandler.emit(x,record) if config['DEBUG'] else None
    config = ConfigManager.getConfig(getEnviron())
    if config['LOG_FILE_OUTPUT']:
        fn = os.path.join(config['LOG_FILE_DIRECTORY'],getEnviron() ) + '.log'
        if config['LOG_FILE_ROTATE']:
            from logging import RotateFileHandler
            handler = RotateFileHandler(fn,'a', config['LOG_ROTATE_MAX_BITE'], config['LOG_ROTATE_COUNT'])
        else:
            from logging import FileHandler
            handler = FileHandler(fn, 'a')

        handler.setFormatter(Formatter(config['LOG_OUTPUT_FORMAT']))
        logger = getLogger()
    else:
        handler = DebugHandler()
        handler.setFormatter(Formatter(config['LOG_DEBUG_FORMAT']))
        logger = getLogger(loggerName)
    
    logger.setLevel(DEBUG)

    del logger.handlers[:]
    logger.__class__ = DebugLogger
    logger.addHandler(handler)
    return logger