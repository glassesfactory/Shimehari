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
    summary = "Clean up *.py[cod]"
    usage = "Usage: %prog COMMAND [OPTIONS]"

    def __init__(self):
        super(Command, self).__init__()

    def handle(self, *args, **options):
        for root, dirs, files in os.walk(os.getcwd()):
            for f in files:
                f = unicode(f, 'cp932')
                if not re.search(r'\.py[cod]$', f):
                    continue
                fullpath = os.path.join(root, f)
                path = root.replace(os.getcwd() + '/', '')
                sys.stdout.write('\033[1;31m    remove \033[0m %s\n' % os.path.join(path, f))
                os.remove(fullpath)
        return 0

Command()
