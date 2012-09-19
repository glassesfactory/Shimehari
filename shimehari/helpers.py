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
from shimehari.shared import currentApp, request, _appContextStack, _requestContextStack
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

u"""-----------------------------
    ::pkg:: Shimehari.helpers
    getHandlerAction
    ~~~~~~~~~~~~~~~~

    [args]
    :resource

        
----------------------------------"""
def getHandlerAction(resource, action):
    try:
        handler = getattr(resource, action)
        if callable(handler):
            return handler
    except AttributeError:
        pass


u"""-----------------------------
    ::pkg:: Shimehari.helpers
    getHostName
    ~~~~~~~~~~~

    URL からホスト名を取得します。
    [args]
    :url
        ホスト名を抜き出したい URL
        
----------------------------------"""
def getHostName(url):
    return urlparse.urlparse(url).netloc



u"""--------------------------------------
    ::pkg:: Shimehari.helpers
    stripTags
    ~~~~~~~~~

    HTML タグを除去
--------------------------------------"""
import sgmllib
class Stripper(sgmllib.SGMLParser):
    def __init__(self):
        sgmllib.SGMLParser.___init__(self)

    def strip(self,htmlTag):
        self.theString = ""
        self.feed(htmlTag)
        self.close()
        return self.theString

    def handleData(self,data):
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
        if endpoint[:1]==('.'):
            endpoint = endpoint[1:]
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
            fn = fn.replace(rootPath, '')[1:].replace('.py','').replace('/', '.')
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
    options.setdefault('conditional',True)
    return sendFile(filename, **options)



def safeJoin(directory, filename):
    filename = os.path.normpath(filename)
    for sep in _osAltSep:
        if sep in filename:
            raise NotFound()
    if os.path.isabs(filename) or filename.startswith('../'):
        raise NotFound()
    return os.path.join(directory, filename)



u"""-----------------------------
    ::pkg:: Shimehari.helpers
    sendFile
    ~~~~~~~~

    静的ファイルをレスポンスとして返します。
    [return]
    :response
        静的ファイル
        
----------------------------------"""
def sendFile(filenameOrFp, mimetype=None, asAttachment=False,
             attachmentFilename=None, addEtags=True,
             cacheTimeout=None, conditional=False):
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
            filname = os.path.join(currentApp.rootPath, filename)
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
        headers.add('Content-Disposition','attachment',filename=attachmentFilename)

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
        ))

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
    return currentApp.responseClass(json.dumps(dict(*args,**kwargs), \
        indent=None if request.is_xhr else 2), mimetype='application/json')



def fillSpace(text, length):
    if len(text) < length:
        num = length - len(text)
        for i in range(num):
            text += ' '
    return text


from threading import RLock
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


u"""--------------------------------------
    Shimehari.helpers._Kouzi
    ~~~~~~~~~~~~~~~~~~~~~~~~
    Shimehari のベーシッククラス
--------------------------------------"""
class _Kouzi(object):
    def __init__( self, importName, appFolder='app', 
                  controllerFolder='controllers', viewFolder=None):
        self.importName = importName
        self.currentEnv = getEnviron()
        
        self.rootPath = getRootPath(self.importName)
        

        from shimehari.configuration import ConfigManager
        config = ConfigManager.getConfig(self.currentEnv)

        if config and self.rootPath == os.getcwd() +'/' + config['APP_DIRECTORY']:
            self.rootPath = os.getcwd()
        
        self.appFolder = config['APP_DIRECTORY'] if config and config['APP_DIRECTORY'] else appFolder
        self.controllerFolder = config['CONTROLLER_DIRECTORY'] if config and \
                                config['CONTROLLER_DIRECTORY'] else controllerFolder
        self.viewFolder = config['VIEW_DIRECTORY'] if config and config['VIEW_DIRECTORY'] else viewFolder

        self._staticFolder = config['ASSETS_DIRECTORY'] if config and config['ASSETS_DIRECTORY'] else None
        self._staticURL = None

    def _getStaticFolder(self):
        if self._staticFolder is not None:
            return os.path.join(self.rootPath, self._staticFolder)
    def _setStaticFolder(self, value):
        self._staticFolder = value
    staticFolder = property(_getStaticFolder, _setStaticFolder)
    del _getStaticFolder, _setStaticFolder

    def _getStaticURL(self):
        if self._staticURL is None:
            if self.staticFolder is None:
                return None
            return '/' + os.path.basename(self.staticFolder)
    def _setStaticURL(self, value):
        self._staticURL = value
    staticURL = property(_getStaticURL, _setStaticURL)
    del _getStaticURL, _setStaticURL



    @property
    def hasStaticFolder(self):
        return self.staticFolder is not None


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
    def sendStaticFile(self, filename):
        if not self.hasStaticFolder:
            raise RuntimeError('static file folder has none.')
        cacheTimeout = self.getSendFileMaxAge(filename)
        return sendFromDirectory(self.staticFolder, filename, cacheTimeout=cacheTimeout)



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
        return open(os.path.join(self.rootPath,filename), mode)

