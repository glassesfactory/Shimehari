#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
===============================
    Shimehari.core.manage.commands.clean
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    clean コマンド

    各コマンドモジュールは共通インターフェースとして
    Command クラスを持ちます。

===============================
"""

import os
import re
import sys
from shimehari.core.manage import AbstractCommand
from shimehari.configuration import ConfigManager

u"""
===============================
    ::pkg:: Shimehari.core.manage.commands.clean
    Command
    ~~~~~~~
    コマンドの実装

===============================
"""


class Command(AbstractCommand):
    name = 'clean'
    summary = "Clean up files"
    usage = "Usage: %prog TARGET"

    targets = ('pyc', 'log')

    def __init__(self):
        super(Command, self).__init__()

    def handle(self, target=None, *args, **options):
        isUnknownTarget = False

        if not target is None and not target in self.targets:
            isUnknownTarget = True
            sys.stdout.write('Unknown target. ')

        if target is None or isUnknownTarget:
            sys.stdout.write('Please imput target.\n')
            for theTarget in self.targets:
                sys.stdout.write('    %s\n' % theTarget)
            return 0

        exec_method = getattr(self, '_exec_%s' % target)
        return exec_method()

    def _exec_pyc(self):
        self._removeFiles(os.getcwd(), r'\.py[cod]$')

    def _exec_log(self):
        __import__('config')
        config = ConfigManager.getConfig()
        logDir = os.path.join(os.getcwd(), config['LOG_FILE_DIRECTORY'])

        self._removeFiles(logDir, r'\.log$')

    def _removeFiles(self, path, fileReg):
        for root, dirs, files in os.walk(path):
            for f in files:
                f = unicode(f, 'cp932')
                if not re.search(fileReg, f):
                    continue
                fullpath = os.path.join(root, f)
                path = root.replace(os.getcwd() + '/', '')
                sys.stdout.write('\033[1;31m    remove \033[0m %s\n' % os.path.join(path, f))
                os.remove(fullpath)
        return 0

Command()
