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
from optparse import OptionParser, make_option

from shimehari.core.manage import AbstractCommand
from shimehari.core.helpers import importFromString
from shimehari.configuration import ConfigManager
from shimehari.core.exceptions import DrinkError, CommandError

DEFAULT_PORT = 5959
DEFAULT_HOST = '127.0.0.1'


class BaseDrinkCommand(AbstractCommand):
    option_list = AbstractCommand.option_list + (
        make_option('--port', '-p', action='store', type='int', dest='port', help='port number.'),
        make_option('--host', action='store', type='string', dest='host', help='host name.'),
        make_option('--debug', '-d', action='store_true', default=False, help='running debug mode.'),
    )

    def __init__(self):
        self.port = DEFAULT_PORT
        self.host = DEFAULT_HOST
        self.debug = False



    def run(self, *args, **options):
        try:
            #humu-
            import config
        except ImportError, e:
            pass

        try:
            currentEnv = options.get('SHIMEHARI_ENV')
            currentConfig = ConfigManager.getConfig(currentEnv or 'development')
            app = importFromString(currentConfig['APP_DIRECTORY'] + '.' + currentConfig['MAIN_SCRIPT'] + '.' + currentConfig['APP_INSTANCE_NAME'])
            app.drink(host=self.host, port=int(self.port), debug=self.debug)
        except Exception, e:
            raise CommandError(e)


    def handle(self, *args, **options):
        port = options.get('port')
        if port:
            self.port = port

        host = options.get('host')
        if not host:
            self.host = host
        self.debug = options.get('debug')
        self.run(*args, **options)

class Command(BaseDrinkCommand):
    def getHandler(self):
        pass