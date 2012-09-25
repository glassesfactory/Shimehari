#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
===============================
    [[Shimehari Config]]
    config
    ~~~~~~

===============================
"""

from datetime import timedelta
from shimehari.configuration import Config, ConfigManager

ConfigManager.addConfigs([
    Config('development', {
        'DEBUG': False,

        'TEST': False,

        'APP_ROOT': None,

        #アプリのディレクトリ名
        'APP_DIRECTORY': 'testApp',

        'MAIN_SCRIPT': 'main',

        #アプリケーションinstanceの名前
        'APP_INSTANCE_NAME': 'app',

        'CONTROLLER_DIRECTORY': 'controllers',

        'VIEW_DIRECTORY': 'views',

        #for daiginjou
        'MODEL_DIRECTORY': 'models',

        'PREFERRED_URL_SCHEME': 'http',

        'AUTO_SETUP': True,

        'TEMPLATE_ENGINE': 'jinja2',

        'USE_X_SENDFILE': False,

        'SECRET_KEY': '_secret_shimehari',

        'SERVER_NAME': None,

        'TRAP_HTTP_EXCEPTIONS': False,

        'TRAP_BAD_REQUEST_ERRORS': False,

        'PRESERVE_CONTEXT_ON_EXCEPTION': None,

        'PERMANENT_SESSION_LIFETIME': timedelta(days=31)
    })
])
