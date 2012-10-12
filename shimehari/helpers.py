#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
===============================
    Shimehari.helpers
    ~~~~~~~~~~~~~~~~~
    便利メソッド
===============================
"""

import os
import sys
import re
import urlparse
import pkgutil
import mimetypes
from time import time
from zlib import adler32
from threading import RLock

u"""json が使用可能かどうか"""
jsonAvailable = True
json = None
try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        try:
            from django.utils import simplejson as json
        except ImportError:
            jsonAvailable = False

from werkzeug.datastructures import Headers
from werkzeug.wsgi import wrap_file
from werkzeug.urls import url_quote
from werkzeug.routing import BuildError
from werkzeug.exceptions import NotFound
from shimehari.shared import session, currentApp, request, _appContextStack, _requestContextStack
from shimehari.core.helpers import importFromString


def _assertHaveJson():
    if not jsonAvailable:
        raise RuntimeError(u'json ないじゃん')

u"""redis が使用可能かどうか"""
redisAvailable = True
redis = None
try:
    import redis
except ImportError:
    redisAvailable = False


def _assertHaveRedis():
    if not redisAvailable:
        raise RuntimeError('no redis module found')


_osAltSep = list(sep for sep in [os.path.sep, os.path.altsep] if sep not in (None, '/'))

_missing = object()

_toJsonFilter = json.dumps


def getHandlerAction(resource, action):
    u"""与えられたコントローラーとアクション名からマッチするハンドラを返します。
    :param resource:    ハンドラを抱えているコントローラー
    :param action:      ハンドラを取得したいアクション
    """
    try:
        handler = getattr(resource, action)
        if callable(handler):
            return handler
    except AttributeError:
        pass


def getHostName(url):
    u"""URL からホスト名を取得します。

    :param url: ホスト名を抜き出したい URL

    """
    return urlparse.urlparse(url).netloc


import sgmllib


class Stripper(sgmllib.SGMLParser):
    u"""与えられたストリングから HTML タグを除去するクラス。"""
    def __init__(self):
        sgmllib.SGMLParser.__init__(self)

    def strip(self, htmlTag):
        self.theString = ""
        self.feed(htmlTag)
        self.close()
        return self.theString

    def handle_data(self, data):
        self.theString += data


def urlFor(endpoint, **values):
    appctx = _appContextStack.top
    reqctx = _requestContextStack.top

    if appctx is None:
        raise RuntimeError('hoge')

    if reqctx is not None:
        urlAdapter = reqctx.urlAdapter
        # if urlAdapter is None:
            # raise RuntimeError('ooooo')
        external = values.pop('_external', False)
    else:
        urlAdapter = appctx.adapter
        if urlAdapter is None:
            raise RuntimeError('url adapter not found')
        external = values.pop('_external', True)

    anchor = values.pop('_anchor', None)
    method = values.pop('_method', None)
    appctx.app.injectURLDefaults(endpoint, values)

    try:
        rv = urlAdapter.build(endpoint, values, method=method, force_external=external)
    except BuildError, error:
        values['_external'] = external
        values['_anchor'] = anchor
        values['_method'] = method
        return appctx.app.handleBuildError(error, endpoint, **values)

    rv = urlAdapter.build(endpoint, values, method=method, force_external=external)

    if anchor is not None:
        rv += '#' + url_quote(anchor)
    return rv


def findPackage(importName):
    rootModName = importName.split('.')[0]
    loader = pkgutil.get_loader(rootModName)
    if loader is None or importName == '__main__':
        pkgPath = os.getcwd()
    else:
        if hasattr(loader, 'get_filename'):
            filename = loader.get_filename(rootModName)
        elif hasattr(loader, 'active'):
            filename = loader.active
        else:
            __import__(importName)
            filename = sys.modules[importName].__file__
        pkgPath = os.path.abspath(os.path.dirname(filename))

        if loader.is_package(rootModName):
            pkgPath = os.path.dirname(pkgPath)

    siteParent, siteFolder = os.path.split(pkgPath)
    pyPrefix = os.path.abspath(sys.prefix)
    if pkgPath.startswith(pyPrefix):
        return pyPrefix, pkgPath
    elif siteFolder.lower() == 'site-packages':
        parent, folder = os.path.split(siteParent)
        if folder.lower == 'lib':
            baseDir = parent
        elif os.path.basename(parent).lower() == 'lib':
            baseDir = os.path.dirname(parent)
        else:
            baseDir = siteParent
        return baseDir, pkgPath
    return None, pkgPath


u"""-----------------------------
    ::pkg:: Shimehari.helpers
    getModulesFromPyFile
    ~~~~~~~~~~~~~~~~~~~~

    Python ファイルからモジュールをインポートします
    [args]
    :targetPath
        インポートしたいモジュール名
    :rootPath

    [return]
    :modules
        インポートされたモジュール

----------------------------------"""
import glob


def getModulesFromPyFile(targetPath, rootPath):
    files = glob.glob(targetPath + '/*.py')
    modules = []
    for fn in files:
        if not '__init__' in fn:
            fn = fn.replace(rootPath, '')[1:].replace('.py', '').replace('/', '.')
            modules.append(fn)
    return modules


u"""-----------------------------
    ::pkg:: Shimehari.helpers
    getRootPath
    ~~~~~~~~~~~

    root パスを取得します
    [args]
    :importName
        インポート時の名前

    [return]
        :string ルートパス

----------------------------------"""


def getRootPath(importName):
    loader = pkgutil.get_loader(importName)
    if loader is None or importName == '__main__':
        return os.getcwd()

    if hasattr(loader, 'get_filename'):
        filePath = loader.get_filename(importName)
    else:
        __import__(importName)
        filePath = sys.modules[importName].__file__
    return os.path.dirname(os.path.abspath(filePath))


u"""-----------------------------
    ::pkg:: Shimehari.helpers
    getEnviron
    ~~~~~~~~~~

    現在の動作環境を取得します。
    [return]
    :url
        ホスト名を抜き出したい URL

----------------------------------"""


def getEnviron():
    if 'SHIMEHARI_WORK_ENV' in os.environ:
        return os.environ['SHIMEHARI_WORK_ENV']
    return 'development'


def sendFromDirectory(directory, filename, **options):
    filename = safeJoin(directory, filename)
    if not os.path.isfile(filename):
        raise NotFound()
    options.setdefault('conditional', True)
    return sendFile(filename, **options)


def safeJoin(directory, filename):
    filename = os.path.normpath(filename)
    for sep in _osAltSep:
        if sep in filename:
            raise NotFound()
    if os.path.isabs(filename) or filename.startswith('../'):
        raise NotFound()
    return os.path.join(directory, filename)


def sendFile(filenameOrFp, mimetype=None, asAttachment=False,
             attachmentFilename=None, addEtags=True,
             cacheTimeout=None, conditional=False):
    u"""静的ファイルをレスポンスとして返します。

    :param filenameOrFp:    送りたいファイル名
    :param mimetype:        mimetype

    """
    mtime = None
    if isinstance(filenameOrFp, basestring):
        filename = filenameOrFp
        file = None
    else:
        from warnings import warn
        file = filenameOrFp
        filename = getattr(file, 'name', None)

        if not attachmentFilename and not mimetype \
           and isinstance(filename, basestring):
            warn(DeprecationWarning('THAAAAAAAA'), stacklevel=2)
        if addEtags:
            warn(DeprecationWarning('AAAAAAA?'), stacklevel=2)

    if filename is not None:
        if not os.path.isabs(filename):
            os.path.join(currentApp.rootPath, filename)
    if mimetype is None and (filename or attachmentFilename):
        mimetype = mimetypes.guess_type(filename or attachmentFilename)[0]
    if mimetype is None:
        mimetype = 'application/octet-stream'

    headers = Headers()
    if asAttachment:
        if attachmentFilename is None:
            if filename is None:
                raise TypeError('file name is invalid')
            attachmentFilename = os.path.basename(filename)
        headers.add('Content-Disposition', 'attachment', filename=attachmentFilename)

    if currentApp.useXSendFile and filename:
        if file is not None:
            file.close()
        headers['X-Sendfile'] = filename
        #for nginx
        #headers['X-Accel-Redirect'] = filename
        data = None
    else:
        if file is None:
            file = open(filename, 'rb')
            mtime = os.path.getmtime(filename)
        data = wrap_file(request.environ, file)

    rv = currentApp.responseClass(data, mimetype=mimetype, headers=headers, direct_passthrough=True)

    if mtime is not None:
        rv.last_modified = int(mtime)

    rv.cache_control.public = True
    if cacheTimeout is None:
        cacheTimeout = currentApp.getSendFileMaxAge(filename)
    if cacheTimeout:
        rv.cache_control.max_age = cacheTimeout
        rv.expires = int(time() + cacheTimeout)

    if addEtags and filename is not None:
        rv.set_etag('Shimehari-%s-%s-%s' %
            (os.path.getmtime(filename),
            os.path.getsize(filename),
            adler32(
                filename.encode('utf8') if isinstance(filename, unicode) else filename
            ) & 0xffffffff
            )
        )

    if conditional:
        rv = rv.make_conditional(request)
        if rv.status_code == 304:
            rv.headers.pop('x-sendfile', None)
    return rv


def jsonify(*args, **kwargs):
    if __debug__:
        _assertHaveJson()
    """
    if 'padded' in kwargs:
        if isinstance(kwargs['padded'], str):
            callback = request.args.get(kwargs['padded']) or 'jsonp'
        else:
            callback = request.args.get('callback') or request.args.get('jsonp') or 'jsonp'
        del kwargs['padded']
        jsonStr = json.dumps(dict(*args,**kwargs), indent=None)
        content = str(callback) + '(' + jsonStr + ')'
        return currentApp.responseClass(content, mimetype='application/javascript')
    """
    resp = json.dumps(dict(*args, **kwargs), indent=None if request.is_xhr else 2)
    return currentApp.responseClass(resp, mimetype='application/json')


def fillSpace(text, length):
    if len(text) < length:
        num = length - len(text)
        for i in range(num):
            text += ' '
    return text


class lockedCachedProperty(object):
    def __init__(self, func, name=None, doc=None):
        self.__name__ = name or func.__name__
        self.__module__ = func.__module__
        self.__doc__ = doc or func.__doc__
        self.func = func
        self.lock = RLock()

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        with self.lock:
            value = obj.__dict__.get(self.__name__, _missing)
            if value is _missing:
                value = self.func(obj)
                obj.__dict__[self.__name__] = value
            return value


def getTemplater(app, templaterName, *args, **options):
    import shimehari
    templateDir = os.path.join(shimehari.__path__[0], 'template', templaterName)
    if not os.path.isdir(templateDir):
        raise ValueError('template engine not found :: %s\n' % templateDir)
    try:
        module = importFromString('shimehari.template.' + templaterName)
        templater = module.templater
    except Exception, e:
        raise Exception(e)
    return templater(app, *args, **options)


def flash(message, category='message'):
    u"""次のリクエストが発生するまで存在する揮発性のあるメッセージ。

    :param message: メッセージ。次のリクエストがあった際には消滅します。
    :param category: カテゴリー

    """
    flashes = session.get('_flashes', [])
    flashes.append((category, message))
    session['_flashes'] = flashes


def getFlashedMessage(withCategory=False, categoryFilter=[]):
    u"""flash に突っ込まれたメッセージを取得します。"""
    flashes = _requestContextStack.top.flash
    if flashes is None:
        _requestContextStack.top.flash = flashes = session.pop('_flashes') if '_flashes' in session else []
    if categoryFilter:
        flashes = filter(lambda f: f[0] in categoryFilter, flashes)
    if not withCategory:
        return [x[1] for x in flashes]
    return flashes


u"""--------------------------------------
    Shimehari.helpers._Kouzi
    ~~~~~~~~~~~~~~~~~~~~~~~~
    Shimehari のベーシッククラス
--------------------------------------"""


class _Kouzi(object):
    def __init__(self, importName, appFolder='app',
                  controllerFolder='controllers', viewFolder=None):
        self.importName = importName
        self.currentEnv = getEnviron()

        self.rootPath = getRootPath(self.importName)

        from shimehari.configuration import ConfigManager
        config = ConfigManager.getConfig(self.currentEnv)

        if config and self.rootPath == os.getcwd() + '/' + config['APP_DIRECTORY']:
            self.rootPath = os.getcwd()

        self.appFolder = config['APP_DIRECTORY'] if config and config['APP_DIRECTORY'] else appFolder
        self.controllerFolder = config['CONTROLLER_DIRECTORY'] if config and \
                                config['CONTROLLER_DIRECTORY'] else controllerFolder
        self.viewFolder = config['VIEW_DIRECTORY'] if config and config['VIEW_DIRECTORY'] else viewFolder

        if config and config['ASSETS_DIRECTORY']:
            if type(config['ASSETS_DIRECTORY']) is list:
                self._staticFolders = {}
                [self._staticFolders.setdefault(x, x) for x in config['ASSETS_DIRECTORY']]
            else:
                self._staticFolders = {config['ASSETS_DIRECTORY']: config['ASSETS_DIRECTORY']}
        else:
            self._staticFolders = {}
        self._staticURLDict = {}

    def getStaticFolder(self, key):
        if key in self._staticFolders:
            return os.path.join(self.rootPath, self.appFolder, self._staticFolders[key])

    def setStaticFolder(self, value):
        self._staticFolders.setdefault(value, value)

    def getStaticFolders(self):
        return self._staticFolders.values()

    def setStaticFolders(self, **folders):
        self._staticFolders.update(folders)

    def getStaticURL(self, key):
        if key in self._staticURLDict:
            return '/' + os.path.basename(self._staticFolders[key])

    def setStaticURL(self, value):
        self._staticURLDict.setdefault(value, value)

    def getStaticURLs(self):
        if len(self._staticURLDict) < 1:
            if len(self._staticFolders) == 0:
                return None
            return ['/' + os.path.basename(x) for x in self._staticFolders]
        return self._staticURLDict.values()

    def setStaticURLs(self, **urls):
        self._staticURLDict.update(urls)

    @property
    def hasStaticFolder(self):
        return len(self._staticFolders) > 0

    u"""-----------------------------
        ::pkg:: Shimehari.helpers._Kouzi
        sendStaticFile
        ~~~~~~~~~~~~~~
        静的ファイルをレスポンスとして返します。

        [args]
        :filename 要求するファイル名

        [return]
        :response レスポンス

    ----------------------------------"""

    from shimehari.shared import request

    def sendStaticFile(self, filename):
        if not self.hasStaticFolder:
            raise RuntimeError('static file folder has none.')
        cacheTimeout = self.getSendFileMaxAge(filename)
        if request is not None and request.urlRule is not None:
            key = request.urlRule.rule.split('/')[1]
            dirname = self.getStaticFolder(key)
        else:
            dirname = filename.split('/')
            if len(dirname) == 1:
                dirname = self.getStaticFolder(self.getStaticFolders()[0])
        return sendFromDirectory(dirname, filename, cacheTimeout=cacheTimeout)

    u"""-----------------------------
        ::pkg:: Shimehari.helpers._Kouzi
        getSendFileMaxAge
        ~~~~~~~~~~~~~~~~~
        静的ファイルをレスポンスとして返します。

        [args]
        :filename 要求するファイル名

        [return]
        :response レスポンス

    ----------------------------------"""
    def getSendFileMaxAge(self, filename):
        return currentApp.config['SEND_FILE_MAX_AGE_DEFAULT']

    def openFile(self, filename, mode='rb'):
        if mode not in ('r', 'rb'):
            raise ValueError('can not read file')
        return open(os.path.join(self.rootPath, filename), mode)
