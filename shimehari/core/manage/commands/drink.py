#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
===============================
    Shimehari.core.manage.commands
    drink
    ~~~~~

    Shimehari App を起動します。

===============================
"""

import os
import sys
import traceback
from optparse import make_option

from shimehari.core.manage import AbstractCommand
from shimehari.core.helpers import importFromString
from shimehari.configuration import ConfigManager
from shimehari.core.exceptions import DrinkError


class BaseDrinkCommand(AbstractCommand):
    name = 'drink'
    summary = 'Present a web page at http://127.0.0.1:5959/'
    usage = "Usage: %prog COMMAND [OPTIONS]"

    option_list = AbstractCommand.option_list + (
        make_option('--port', '-p', action='store', type='int', dest='port', default=5959, help='port number. default %default'),
        make_option('--host', action='store', type='string', dest='host', default='127.0.0.1', help='host name. default %default'),
        make_option('--debug', '-d', action='store_true', default=False, help='running debug mode.'),
        make_option('--browser', '-b', action='store_true', dest='browser', default=False, help='open browser.')
    )

    def __init__(self):
        super(BaseDrinkCommand, self).__init__()
        self.debug = False

    def run(self, *args, **options):
        try:
            #humu-
            import config
        except ImportError, e:
            sys.path.append(os.getcwd())
            try:
                import config
            except ImportError, e:
                t = sys.exc_info()[2]
                raise DrinkError(u'ちょっと頑張ったけどやっぱりコンフィグが見当たりません。\n%s' % e), None, traceback.print_exc(t)

        try:
            currentEnv = options.get('SHIMEHARI_ENV')
            currentConfig = ConfigManager.getConfig(currentEnv or 'development')
            app = importFromString(currentConfig['APP_DIRECTORY'] + '.' + currentConfig['MAIN_SCRIPT'] + '.' + currentConfig['APP_INSTANCE_NAME'])
            if not self.debug and currentConfig['DEBUG']:
                self.debug = True

            if options.get('browser'):
                def openBrowser(host, port):
                    url = 'http://' + host + ':' + str(port)
                    import webbrowser
                    webbrowser.open(url)
                import threading
                timer = threading.Timer(0.5, openBrowser, args=[self.host, self.port])
                timer.start()
            app.drink(host=self.host, port=int(self.port), debug=self.debug)

        except Exception, e:
            t = sys.exc_info()[2]
            raise DrinkError(u'飲めるかと思ったのですが嘔吐しました。\n%s' % e), None, traceback.print_exc(t)

    def handle(self, *args, **options):
        self.port = options.get('port')
        self.host = options.get('host')
        self.debug = options.get('debug')
        self.run(*args, **options)

BaseDrinkCommand()


class Command(BaseDrinkCommand):
    def getHandler(self):
        pass
