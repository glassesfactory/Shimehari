#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
===============================
    Shimehari.core.manage.commands.routes
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    現在のルーティング状況をコマンドラインへダンプします。

===============================
"""

import os
import sys
import traceback

from shimehari.core.exceptions import CommandError
from shimehari.core.manage import AbstractCommand
from shimehari.core.helpers import importFromString
from shimehari.configuration import ConfigManager, Config
from shimehari.helpers import getEnviron


class Command(AbstractCommand):
    name = 'routes'
    summary = "Show Application routing"
    usage = "Usage: %prog [OPTIONS]"

    def __init__(self):
        super(Command, self).__init__()

    def handle(self, *args, **options):
        try:
            importFromString('config')
        except ImportError:
            sys.path.append(os.getcwd())
            try:
                importFromString('config')
            except ImportError, e:
                t = sys.exc_info()[2]
                raise CommandError(u'コンフィグファイルが見当たりません:: %s' % e), None, traceback.print_tb(t)

        config = ConfigManager.getConfig(getEnviron())
        appPath = os.path.join(os.getcwd(), config['APP_DIRECTORY'])
        if not os.path.isdir(appPath):
            t = sys.exc_info()[2]
            raise CommandError(u'アプリケーションが見当たりません::'), None, traceback.print_tb(t)

        try:
            router = importFromString(config['APP_DIRECTORY'] + '.' + 'router')
        except Exception, e:
            t = sys.exc_info()[2]
            raise CommandError(u'ルーターがみつかりません。\n %s' % e), None, traceback.print_tb(t)

        sys.stdout.write('\nYour Shimehari App Current Routing.\n\n')
        sys.stdout.write('Methods       |URL                          |Action\n')
        sys.stdout.write('----------------------------------------------------------------------\n')
        sys.stdout.write(router.appRoutes.dump())
        sys.stdout.write('\n')

Command()
