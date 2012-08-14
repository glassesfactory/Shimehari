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
        'DEBUG':False,

        'TEST':False,

        #アプリのディレクトリ名
        'APP_DIRECTORY':'%s',

        'MAIN_SCRIPT':'main',

        #アプリケーションinstanceの名前
        'APP_INSTANCE_NAME':'app',

        'CONTROLLER_DIRECTORY':'controllers',

        'VIEW_DIRECTORY':'views',

        #for daiginjou
        'MODEL_DIRECTORY':'models',

        'PREFERRED_URL_SCHEME':'http',

        'AUTO_SETUP':True,

        'TEPMLATE_ENGINE':'jinja2',

        'SECRET_KEY':'_secret_shimehari',

        'SERVER_NAME':None,

        'PRESERVE_CONTEXT_ON_EXCEPTION':None,

        'PERMANENT_SESSION_LIFETIME':timedelta(days=31)
    })
])