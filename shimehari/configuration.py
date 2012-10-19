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


class ConfigManager(object):
    u"""Config インスタンスを管理します。"""

    configrations = {}

    @classmethod
    def hasConfig(cls):
        u"""Config インスタンスが登録されているかどうか

        :param bool: Config インスタンスが登録されているかどうかを返します。
        """
        if not cls.configrations or len(cls.configrations) < 1:
            return False
        else:
            return True

    @classmethod
    def getConfigs(cls):
        u"""Config インスタンスが格納されたディクショナリを返します。"""
        return cls.configrations

    @classmethod
    def getConfig(cls, environ=None):
        u"""Config インスタンスを取得します。

        :param environ: 取得したい環境。
                        指定されない場合は現在の環境に合わせた Config が返されます。
        """
        if environ is None:
            environ = getEnviron()
        if environ in cls.configrations:
            return cls.configrations[environ]
        return None

    @classmethod
    def addConfigs(cls, configs=[]):
        u"""複数の Config インスタンスをまとめて登録します。

        :param configs: Config インスタンスを格納したディクショナリ
        """
        [cls.addConfig(c) for c in configs]

    @classmethod
    def addConfig(cls, config):
        u"""Config インスタンスを登録します。

        :param config: 登録したいコンフィグインスタンス
        """
        if isinstance(config, Config):
            cls.configrations.setdefault(config.environment, config)
        else:
            raise TypeError('config じゃない')

    @classmethod
    def removeConfig(cls, environment):
        u"""Config インスタンスを削除します。

        :param enviroment: 削除したい環境
        """
        if cls.configrations[environment]:
            cls.configrations.pop(environment)


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
    u"""Config クラスはアプリケーションの設定を保存します。
    初期値として、以下の設定を保持しています。

    :param DEBUG: アプリケーションをデバッグモードとして起動するかどうか。
                  この項目が True に指定された場合、アプリケーションは常にデバッグモードで起動されます。
                  一時的にデバッグモードで起動したい場合は以下のコマンドを用いたほうが便利です。

                  ::

                    $ shimehari drink -d

    :param TEST:                            アプリケーションをテストモードとして起動するかどうか。
    :param APP_ROOT:                        アプリケーションのルートディレクトリを指定します。
    :param APP_DIRECTORY:                   アプリケーションのファイルが置かれたディレクトリを指定します。
    :param MAIN_SCRIPT:                     アプリケーションで一番最初に実行されるスクリプトを指定します。
    :param APP_INSTANCE_NAME:               アプリケーションがインスタンス化される際の名前を指定します。
    :param CONTROLLER_DIRECTORY:            コントローラーが格納されたディレクトリを指定します。
    :param VIEW_DIRECTORY:                  ビューファイルが格納されたディレクトリを指定します。
    :param MODEL_DIRECTORY:                 モデルファイルが格納されたディレクトリを指定します。
    :param ASSETS_DIRECTORY:                アセットファイルが格納されたディレクトリを指定します。
    :param STATIC_DIRECTORY:                静的ファイルが格納されたディレクトリを指定します。
    :param PREFERRED_URL_SCHEME:            URL を発行する際のプロトコルを指定します。
    :param AUTO_SETUP:                      自動的にセットアップを開始するかどうか指定します。
                                            この項目についての詳細は app.setup を参照してください。
    :param CONTROLLER_AUTO_NAMESPACE:       コントローラーディレクトリ内で、サブディレクトリが作成されていた場合、
                                            自動的にサブディレクトリ名を URL に反映させるかどうかを決定します。
    :param TEMPLATE_ENGINE:                 デフォルトで使用するテンプレートエンジンを決定します。
    :param USE_X_SENDFILE:                  静的ファイルを X-Sendfile を使用して返すかどうか指定します。
    :param SECRET_KEY:                      アプリケーション固有のシークレットキーです。アプリケーションごとに変更してください。
    :param SERVER_NAME:                     ホスト名を指定します。
    :param TRAP_HTTP_EXCEPTIONS:            hoge
    :param TRAP_BAD_REQUEST_ERRORS:         huga
    :param PRESERVE_CONTEXT_ON_EXCEPTION:   aaa
    :param SEND_FILE_MAX_AGE_DEFAULT:       静的ファイルのタイムアウトを指定します。
    :param PERMANENT_SESSION_LIFETIME:      セッションの有効期限を指定します。
    :param SESSION_COOKIE_NAME:             aaa
    :param SESSION_COOKIE_HTTPONLY:         iii
    :param SESSION_COOKIE_SECURE:           uuu
    :param CACHE_STORE:                     標準で使用するキャッシュストアを指定します。
    :param CACHE_DEFAULT_TIMEOUT:           キャッシュとして保持するデフォルトの時間を指定します。
    :param CACHE_THRESHOLD:                 キャッシュの保持数を指定します。
    :param CACHE_KEY_PREFIX:                キャッシュとして格納するキーに対して接頭詞を指定します。
    :param CACHE_DIR:                       FileSystemCacheStore を使用する際、キャッシュの保存先を指定します。
    :param CACHE_OPTIONS:                   キャッシュストアインスタンス化時に渡すオプションを指定します。
    :param CACHE_ARGS:                      キャッシュストアインスタンス化時に渡す引数を指定します。
    :param LOG_FILE_OUTPUT:                 ログを外部ファイルとして出力するかどうか指定します。
    :param LOG_FILE_ROTATE:                 ログを外部ファイルとして出力する際、ログローテートするかどうか
    :param LOG_ROTATE_MAX_BITE:             ログローテートする場合、最大ファイルサイズを指定します。
    :param LOG_ROTATE_COUNT:                ログローテートする場合、過去の差分として何ファイルまで残すのか指定します。
    :param LOG_FILE_DIRECTORY:              ログファイルの出力先を指定します。
    :param LOG_DEBUG_FORMAT:                ログをコンソール上に出力する際のフォーマットを指定します。
    :param LOG_OUTPUT_FORMAT:               ログをファイルに出力する際のフォーマットを指定します。
    """
    defaults = {
        'DEBUG': False,
        'TEST': False,
        'APP_ROOT': None,
        'APP_DIRECTORY': 'app',
        'MAIN_SCRIPT': 'main',
        'APP_INSTANCE_NAME': 'app',
        'CONTROLLER_DIRECTORY': 'controllers',
        'VIEW_DIRECTORY': 'views',
        'MODEL_DIRECTORY': 'models',
        'ASSETS_DIRECTORY': 'assets',
        'STATIC_DIRECTORY': [],
        'PREFERRED_URL_SCHEME': 'http',
        'AUTO_SETUP': True,
        'CONTROLLER_AUTO_NAMESPACE': True,
        'TEMPLATE_ENGINE': 'jinja2',
        'USE_X_SENDFILE': False,
        'SECRET_KEY': '_secret_shimehari',
        'SERVER_NAME': None,
        'TRAP_HTTP_EXCEPTIONS': False,
        'TRAP_BAD_REQUEST_ERRORS': False,
        'PRESERVE_CONTEXT_ON_EXCEPTION': None,
        'SEND_FILE_MAX_AGE_DEFAULT': 12 * 60 * 60,
        'SESSION_COOKIE_NAME': 'session',
        'SESSION_COOKIE_HTTPONLY': True,
        'SESSION_COOKIE_SECURE': False,
        'PERMANENT_SESSION_LIFETIME': timedelta(days=31),
        #キャッシュ
        'CACHE_STORE': None,
        'CACHE_DEFAULT_TIMEOUT': 300,
        'CACHE_THRESHOLD': 500,
        'CACHE_KEY_PREFIX': None,
        'CACHE_DIR': None,
        'CACHE_OPTIONS': None,
        'CACHE_ARGS': [],
        #ログ周り
        'LOG_FILE_OUTPUT': False,
        'LOG_FILE_ROTATE': False,
        'LOG_ROTATE_MAX_BITE': (5 * 1024 * 1024),
        'LOG_ROTATE_COUNT': 5,
        'LOG_FILE_DIRECTORY': 'app/log',
        'LOG_DEBUG_FORMAT': ('-' * 80 + '\n' +
        '%(levelname)s in %(module)s [%(pathname)s:%(lineno)d]:\n' +
        '%(message)s\n' +
        '-' * 80),
        'LOG_OUTPUT_FORMAT': (
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
        u"""現在の設定状況を出力します。"""
        _conf = ''
        for k, v in self.defaults.items():
            _conf += k + ' => ' + str(v) + '\n'
        return _conf
