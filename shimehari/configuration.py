#!/usr/bin/env python
# -*- coding: utf-8 -*-

from shimehari.helpers import getEnviron

u"""
===============================
    Shimehari.configuration
    ~~~~~~~~~~~~~~~~~~~~~~~

    アプリケーション内の様々な設定や環境情報を保持する
    Config クラスを提供します。
    
===============================
"""

ENVIROMENTS = ['development', 'production']



u"""
===============================
    ::pkg:: Shimehari.coniguration

    ConfigManager
    ~~~~~~~~~~~~~
    Config インスタンスを管理します。
    
===============================
"""
class ConfigManager(object):
    configrations = {}

    u"""-----------------------------
        [[classmethod]]
        ::pkg:: Shimehari.configrations.ConfigManager
        hasConfig
        ~~~~~~~~~

        Config インスタンスが登録されているかどうか
        [return]
            :bool 登録されているかどうか
    ------------------------------"""
    @classmethod
    def hasConfig(cls):
        if not cls.configrations or len(cls.configrations) < 1:
            return False
        else:
            return True


    u"""-----------------------------
        [[classmethod]]
        ::pkg:: Shimehari.configrations.ConfigManager
        hasConfig
        ~~~~~~~~~

        Config インスタンスが登録されているかどうか
        [return]
            :bool 登録されているかどうか
    ------------------------------"""
    @classmethod
    def getConfigs(cls):
        return cls.configrations



    u"""-----------------------------
        [[classmethod]]
        ::pkg:: Shimehari.configrations.ConfigManager
        getConfig
        ~~~~~~~~~

        Config インスタンスを取得します
        [args]
            :environ キーとなる環境
        [return]
            :Config
    ------------------------------"""
    @classmethod
    def getConfig(cls, environ=None):
        if environ is None:
            environ = getEnviron()
        if environ in cls.configrations:
            return cls.configrations[environ]
        return None



    u"""-----------------------------
        [[classmethod]]
        ::pkg:: Shimehari.configrations.ConfigManager
        addConfigs
        ~~~~~~~~~~

        Config インスタンスをまとめて登録します
        [args]
            :configs Config インスタンスを格納したディクショナリ

    ------------------------------"""
    @classmethod
    def addConfigs(cls,configs=[]):
        [cls.addConfig(c) for c in configs]



    u"""-----------------------------
        [[classmethod]]
        ::pkg:: Shimehari.configrations.ConfigManager
        addConfig
        ~~~~~~~~~

        Config インスタンスを登録します。
        [args]
            :config 登録したいコンフィグインスタンス
            
    ------------------------------"""
    @classmethod
    def addConfig(cls, config):
        if isinstance(config, Config):
            cls.configrations.setdefault(config.environment,config)
        else:
            raise TypeError('config じゃない')


    @classmethod
    def removeConfig(cls,environment):
        if cls.configrations[environment]:
            cls.configrations.pop(environment)


    """0.2
    @classmethod
    def current(cls):
        return config
    """


u"""
===============================
    ::pkg:: Shimehari.coniguration
    
    Config
    ~~~~~~
    アプリケーションな設定や環境情報を保持する
    コンフィグクラス
    
===============================
"""
from datetime import timedelta
class Config(dict):
    defaults ={
        'DEBUG':False,
        'TEST':False,
        'APP_ROOT':None,
        'APP_DIRECTORY':'app',
        'MAIN_SCRIPT':'main',
        'APP_INSTANCE_NAME':'app',
        'CONTROLLER_DIRECTORY':'controllers',
        'VIEW_DIRECTORY':'views',
        'MODEL_DIRECTORY':'models',
        'ASSETS_DIRECTORY':'assets',
        'PREFERRED_URL_SCHEME':'http',
        'AUTO_SETUP':True,
        'CONTROLLER_AUTO_NAMESPACE':True,
        'TEMPLATE_ENGINE':'jinja2',
        'USE_X_SENDFILE':False,
        'SECRET_KEY':'_secret_shimehari',
        'SERVER_NAME':None,
        'TRAP_HTTP_EXCEPTIONS':False,
        'TRAP_BAD_REQUEST_ERRORS':False,
        'PRESERVE_CONTEXT_ON_EXCEPTION':None,
        'SEND_FILE_MAX_AGE_DEFAULT': 12 * 60 * 60,
        'PERMANENT_SESSION_LIFETIME':timedelta(days=31),
        #キャッシュ
        'CACHE_STORE':None,
        'CACHE_DEFAULT_TIMEOUT': 300,
        'CACHE_THRESHOLD':500,
        'CACHE_KEY_PREFIX':None,
        'CACHE_DIR':None,
        'CACHE_OPTIONS':None,
        'CACHE_ARGS':[],
        #ログ周り
        'LOG_FILE_OUTPUT':False,
        'LOG_FILE_ROTATE':False,
        'LOG_ROTATE_MAX_BITE':(5*1024*1024),
        'LOG_ROTATE_COUNT':5,
        'LOG_FILE_DIRECTORY':'app/log',
        'LOG_DEBUG_FORMAT':('-' * 80 + '\n' +
        '%(levelname)s in %(module)s [%(pathname)s:%(lineno)d]:\n' +
        '%(message)s\n' +
        '-' * 80),
        'LOG_OUTPUT_FORMAT':(
        '%(asctime)s %(levelname)s in %(module)s [%(pathname)s:%(lineno)d]:\n' +
        '%(message)s\n' +
        '-' * 80)
    }


    def __init__(self, environment='development', defaults={}):
        d = self.defaults.copy()
        d.update(defaults)
        dict.__init__(self, d)
        self.environment = environment

    def dump(self):
        _conf = ''
        for k, v in self.defaults.items():
            _conf += k + ' => ' + str(v) + '\n'
        return _conf


