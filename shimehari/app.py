#!/usr/bin/env python
# -*- coding: utf-8 -*-
u"""
===============================
    Shimehari.app
    ~~~~~~~~~~~~~
    Flask などなど参考に。
    ルーティングが多少複雑になっても
    対応できるような作りにしたいなぁ
===============================
"""

import os
import sys
from  threading import Lock, RLock
from functools import update_wrapper
from datetime import timedelta

from werkzeug.exceptions import NotFound, HTTPException, InternalServerError, MethodNotAllowed, BadRequest
from werkzeug.datastructures import ImmutableDict
from werkzeug.routing import RequestRedirect, Rule

from .helpers import _Kouzi, findPackage, getHandlerAction, getModulesFromPyFile, getEnviron, \
                     lockedCachedProperty, getTemplater
from .contexts import RequestContext, AppContext
from .routing import Router
from core.config import RESTFUL_ACTIONS
from .wrappers import Request, Response
from shimehari.configuration import Config, ConfigManager
from shimehari.session import SessionStore
from shimehari.shared import _requestContextStack, _appContextStack, _SharedRequestClass, request
from shimehari.template import _defaultTemplateCtxProcessor
from shimehari.core.exceptions import ShimehariException, ShimehariSetupError
from shimehari.core.signals import appContextTearingDown, requestContextTearingDown


_loggerLock = Lock()

def setupMethod(f):
    def wrapperFunc(self, *args,**kwargs):
        if self.debug or self._gotFirstRequest:
            raise AssertionError('Setup seems to have already completed ...')
        return f(self, *args, **kwargs)
    return update_wrapper(wrapperFunc, f)


class Shimehari(_Kouzi):

    currentEnv = getEnviron()
    debug = None
    testing = None

    requestClass = Request
    responseClass = Response

    testClientCls = None

    teardownAppContextFuncs = []

    defaultConfig = {
        'DEBUG':False,
        'TEST':False,
        'APP_DIRECTORY':'app',
        'CONTROLLER_DIRECTORY':'controllers',
        'VIEW_DIRECTORY':'views',
        #for daiginjou
        'MODEL_DIRECTORY':'models',
        'PREFERRED_URL_SCHEME':'http',
        'AUTO_SETUP':True,
        'TEMPLATE_ENGINE':'jinja2',
        'TRAP_HTTP_EXCEPTIONS':False,
        'SERVER_NAME':None,
        'PERMANENT_SESSION_LIFETIME':timedelta(days=31),
        'SECRET_KEY':'_secret_shimehari'
    }

    templateOptions = {}

    sessionStore = SessionStore()

    sharedRequestClass = _SharedRequestClass

    def __init__(self, importName, 
                 staticURL=None, staticFolder='static',
                 appFolder='app', controllerFolder='controllers', 
                 viewFolder='views', assetsFolder='assets',
                 instancePath=None, isRelativeConfig=False,templateOptions={}):

        _Kouzi.__init__(self, importName, appFolder=appFolder, 
                        controllerFolder=controllerFolder, viewFolder=viewFolder)
        
        if instancePath is None:
            self._instancePath = self.getInstancePath()

        self._logger = None
        self.loggerName = self.importName

        self.config = self.getConfig()


        self.controllers = {}
        self.urlValuePreprocesors = {}
        self.beforeRequestFuncs = {}
        self.beforeFirstRequestFuncs = []
        self.urlDefaultFuncs = {}
        self.afterRequestFuncs = {}
        self._errorHandlers = {}
        self.errorHandlerSpec = {None:self._errorHandlers}
        self.buildErrorHandlers = None
        self.teardownRequestContextFuncs = {}

        self.templateContextProcessors = {
            None: [_defaultTemplateCtxProcessor]
        }

        #CSRF
        from shimehari.crypt import CSRF
        self.csrf = CSRF(self)

        self._router = Router()

        self._gotFirstRequest = False

        self._beforeRequestLock = Lock()

        self.debug = self.config['DEBUG']
        self.test = self.config['TEST']
        self.sessionKey = self.config['SECRET_KEY']
        self.useXSendFile = self.config['USE_X_SENDFILE']

        self.templateOptions = templateOptions
        
        if self.config['AUTO_SETUP']:
            self.setup()


    @property
    def gotFirstRequest(self):        
        return self._gotFirstRequest



    @property
    def propagateExceptions(self):
        return self.testing or self.debug



    @property
    def preserveContextOnException(self):
        rv = self.config['PRESERVE_CONTEXT_ON_EXCEPTION']
        if rv is not None:
            return rv
        return self.debug


    @property
    def logger(self):
        if self._logger and self._logger.name == self.loggerName:
            return self._logger
        with _loggerLock:
            if self._logger and self._logger.name == self.loggerName:
                return self._logger
            from shimehari.logging import createLogger
            self._logger = rv = createLogger(self.loggerName)
            return rv


    u"""--------------------------------------
        ルーティング
    --------------------------------------"""
    def router():
        doc = "The router property."
        def fget(self):
            return self._router
        def fset(self, value):
            self.setControllerFromRouter(value)
            self._router = value
        def fdel(self):
            self.controllers = {}
            del self._router
        return locals()
    router = property(**router())



    """
    ===============================
        methods
    ===============================
    """

    u"""-----------------------------
        ::pkg:: Shimehari.app
        getInstancePath
        ~~~~~~~~~~~~~~~

        インスタンスパスを返します。
        [return]
            :str インスタンスパス
    ------------------------------"""
    def getInstancePath(self):
        prefix, pkgPath = findPackage(self.importName)
        if prefix is None:
            return os.path.join(pkgPath, 'instance')
        return os.path.join(prefix, 'var', self.name + '-instance')



    u"""-----------------------------
        ::pkg:: Shimehari.app
        getConfig
        ~~~~~~~~~

        現在の コンフィグ を返します。
        [return]
            :Config 現在のコンフィグ
    ------------------------------"""
    def getConfig(self):
        configs = ConfigManager.getConfigs()
        try:
            from .config import config
            configs = ConfigManager.getConfigs()
        except ImportError:
            pass
        if not configs:
            cfg = Config(self.currentEnv, self.defaultConfig)
            ConfigManager.addConfig(cfg)
            return cfg
        else:
            return configs[self.currentEnv]



    def saveSession(self, session, response):
        if session.should_save:
            self.sessionStore.save(session, response)
            response.set_cookie(self.sessionKey, session.sid)
        return response



    def openSession(self, request):
        sid = request.cookies.get(self.sessionKey, None)
        if sid is None:
            return self.sessionStore.new()
        else:
            return self.sessionStore.get(sid)


    u"""-----------------------------
        ::pkg:: Shimehari.app
        setControllerFromRouter
        ~~~~~~~~~~~~~~~~~~~~~~~

        ルーターからコントローラーを設定します。
        [args]
        :router
            るーたー
    ------------------------------"""
    def setControllerFromRouter(self, router):
        if not self.controllers:
            self.controllers = {}
        for rule in router._rules:
            self.controllers[rule.endpoint] = rule.endpoint



    u"""-----------------------------
        ::pkg:: Shimehari.app
        addController
        ~~~~~~~~~~~~~

        [args]
        :controller
            追加したいコントローラー
            追加されたコントローラーは
            アプリケーションの管理下に置かれ、
            ルーティングが自動生成されます。
    ------------------------------"""
    def addController(self, controller):
        for action in RESTFUL_ACTIONS:
            handler = getHandlerAction(controller, action)
            if handler is not None:
                self.controllers[handler] = handler



    def addRoute(self, url, func, methods=None, **options):
        rule = Rule(url, endpoint=func.__name__, methods=methods)
        self.controllers[func.__name__] = func
        self.router.add(rule)



    def logException(self, excInfo):
        self.logger.error('excepts on %s [%s]' % (request.path, request.method), exc_info=excInfo)



    def injectURLDefaults(self, endpoint, values):
        funcs = self.urlDefaultFuncs.get(None,())
        for func in funcs:
            func(endpoint, vlaues)



    @lockedCachedProperty
    def templateLoader(self):
        return self.templater.templateLoader



    @lockedCachedProperty
    def templateEnv(self):
        rv = self.templater.templateEnv()
        return rv



    def createTemplateEnvironment(self):
        rv = self.templater.createTemplateEnvironment()
        return rv



    def createGlobalTemplateLoader(self):
        return self.templater.dispatchLoader(self)



    def updateTemplateContext(self,context):
        self.templater.updateTemplateContext(context)



    u"""-----------------------------
        ::pkg:: Shimehari.app
        setup
        ~~~~~

        アプリケーションをセットアップします。
        指定された app ディレクトリ配下にある
        コントローラー、ルーターを探し出しバインドします。

    ------------------------------"""
    def setup(self):
        self.appPath = os.path.join(self.rootPath, self.appFolder)
        if not os.path.isdir(self.appPath):
            raise ShimehariSetupError('Application directory is not found\n%s' % self.rootPath)
            sys.exit(0)
        try:
            apps = __import__(self.appFolder)
            self.setupTemplater()
            self.setupBindController()
            self.setupBindRouter()
        except (ImportError, AttributeError):
            raise ShimehariSetupError('Application directory is invalid')


    def setupTemplater(self):
        try:
            self.templater = getTemplater(self, self.config['TEMPLATE_ENGINE'],templateOptions=self.templateOptions)
        except Exception, e:
            raise ShimehariSetupError('setup template engine was failed... \n%s' % e)

    u"""-----------------------------
        ::pkg:: Shimehari.app
        setupBindController
        ~~~~~~~~~~~~~~~~~~~

        コントローラーをバインドします
        
    ------------------------------"""
    def setupBindController(self):
        self.controllerPath = os.path.join(self.appPath, self.controllerFolder)
        if not os.path.isdir(self.controllerPath):
            raise ShimehariSetupError('Controller in the specified directory does not exist. %s' % self.controllerPath)

        try:
            ctrlDir = self.appFolder + '.' + self.controllerFolder
            ctrlMod = __import__(ctrlDir)
            ctrls = getModulesFromPyFile(self.controllerPath, self.rootPath)
        except (ImportError, AttributeError), error:
            raise ShimehariSetupError('setup controller was failed... \n%s' % error)



    u"""-----------------------------
        ::pkg:: Shimehari.app
        setupBindRouter
        ~~~~~~~~~~~~~~~

        ルーターをバインドします

    ------------------------------"""
    def setupBindRouter(self):
        try:
            routerFile = self.appFolder + '.' + 'router'
            routerMod = __import__(routerFile, fromlist=['router'])
            if hasattr(routerMod, 'appRoutes'):
                self.router = routerMod.appRoutes
        except (ImportError, AttributeError), e:
            raise ShimehariSetupError('Failed to setup the router ...\n details::\n%s' % e)



    u"""-----------------------------
        ::pkg:: Shimehari.app
        beforeRequest
        ~~~~~~~~~~~~~

        リクエスト処理を行う前にする処理を
        登録します。
        [args]
        :f
            実行したい処理
        [return]
        :function
            登録した処理
    ------------------------------"""
    @setupMethod
    def beforeRequest(self, f):
        self.beforeRequestFuncs.setdefault(None,[]).append(f)
        return f



    u"""-----------------------------
        ::pkg:: Shimehari.app
        beforeFirstRequest
        ~~~~~~~~~~~~~~~~~~

        最初のリクエスト処理を行う前にする処理
        [args]
        :f
            実行したい処理
    ------------------------------"""
    @setupMethod
    def beforeFirstRequest(self, f):
        self.beforeFirstRequestFuncs.append(f)



    u"""-----------------------------
        ::pkg:: Shimehari.app
        afterRequest
        ~~~~~~~~~~~~

        リクエストの後に処理
        [args]
        :f
            実行したい処理
    ------------------------------"""
    @setupMethod
    def afterRequest(self, f):
        self.afterRequestFuncs.setdefault(None,[]).append(f)
        return f



    u"""-----------------------------
        ::pkg:: Shimehari.app
        urlValuePreprocessor
        ~~~~~~~~~~~~~~~~~~~~

        リクエストの前に処理
        [args]
        :f
            実行したい処理
    ------------------------------"""
    @setupMethod
    def urlValuePreprocessor(self, f):
        self.urlValuePreprocesors.setdefault(None, []).append(f)
        return f



    @setupMethod
    def tearDownAppContext(self, f):
        self.teardownAppContextFuncs.append(f)
        return f


    @setupMethod
    def errorHandler(self, codeOrException):
        def decorator(f):
            self._registerErrorHandler(None, codeOrException, f)
            return f
        return decorator

    @setupMethod
    def _registerErrorHandler(self, key, codeOrException, f):
        if isinstance(codeOrException, HTTPException):
            codeOrException = codeOrException.code
        if isinstance(codeOrException, (int, long)):
            assert codeOrException != 500 or key is None
            self.errorHandlerSpec.setdefault(key, {})[codeOrException] = f
        else:
            self.errorHandlerSpec.setdefault(key, {}).setdefault(None,[]).append((codeOrException, f))


    u"""-----------------------------
        ::pkg:: Shimehari.app
        tryTriggerBeforeFirstRequest
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        最初のリクエストがあった時のみに行う処理を実行します。
    ------------------------------"""
    def tryTriggerBeforeFirstRequest(self):
        if self._gotFirstRequest:
            return 
        with self._beforeRequestLock:
            if self._gotFirstRequest:
                return 
            self._gotFirstRequest = True
            [f() for f in self.beforeFirstRequestFuncs]



    u"""-----------------------------
        ::pkg:: Shimehari.app
        createAdapter
        ~~~~~~~~~~~~~

        url adapter を生成します
        [args]
        :request
            元となるリクエスト
        [return]
        :adapter
            アダプター
    ------------------------------"""
    def createAdapter(self, request):
        if request is not None:
            return self.router.bind_to_environ(request.environ)
        #なんのこっちゃ
        if self.config['SERVER_NAME'] is not None:
            return self.router.bind(
                self.config['SERVER_NAME'], 
                script_name=self.config['APP_ROOT'] or '/',
                url_scheme=self.config['PREFERRED_URL_SCHEME'])



    u"""-----------------------------
        ::pkg:: Shimehari.app
        appContext
        ~~~~~~~~~~
        アプリケーションコンテキストを返します。
        [args]
        :environ
            環境変数
    ------------------------------"""
    def appContext(self):
        return AppContext(self)



    u"""-----------------------------
        ::pkg:: Shimehari.app
        requestContext
        ~~~~~~~~~~~~~~
        リクエストコンテキストを返します。
        [args]
        :environ
            リクエスト環境変数
    ------------------------------"""
    def requestContext(self,environ):
        return RequestContext(self, environ)



    u"""-----------------------------
        ::pkg:: Shimehari.app
        doAppContextTearDonw
        ~~~~~~~~~~~~~~~~~~~~
        アプリケーションコンテキストがティアーダウンしたとき実行します。
        [args]
        :exc
            
    ------------------------------"""
    def doAppContextTearDonw(self,exc=None):
        if exc is None:
            exc = sys.exc_info()[1]
        for func in reversed(self.teardownAppContextFuncs):
            func(exc)
        appContextTearingDown.send(self, exc)



    u"""-----------------------------
        ::pkg:: Shimehari.app
        doRequestContextTearDown
        ~~~~~~~~~~~~~~
        リクエストコンテキストを返します。
        未実装
        [args]
        :environ
            環境変数
    ------------------------------"""
    def doRequestContextTearDown(self,exc=None):
        if exc is None:
            exc = sys.exc_info()[1]
        for func in reversed(self.teardownRequestContextFuncs.get(None,())):
            rv = func(exc)
        requestContextTearingDown.send(self,exc=exc)



    u"""-----------------------------
        ::pkg:: Shimehari.app
        preprocessRequest
        ~~~~~~~~~~~~~~~~~

        リクエスト前に実行したい処理たちを実行します。
        [return]
        :rv
            登録した処理
    ------------------------------"""
    def preprocessRequest(self):
        for func in self.urlValuePreprocesors.get(None, ()):
            func(request.endpoint, request.viewArgs) 
        self.csrf.checkCSRFExempt()
        self.csrf.csrfProtect()
        for func in self.beforeRequestFuncs.get(None, ()):
            rv = func()
            if rv is not None:                
                return rv



    u"""-----------------------------
        ::pkg:: Shimehari.app
        processResponse
        ~~~~~~~~~~~~~~~
        レスポンス前に行いたい処理を実行します。
        [return]
        :response
            レスポンス
    ------------------------------"""
    def processResponse(self,response):
        context = _requestContextStack.top
        funcs = ()

        if None in self.afterRequestFuncs:
            funcs = self.afterRequestFuncs[None]
        for handler in funcs:
            response = handler(response)
        
        if not self.sessionStore.isNullSession(context.session):
            self.saveSession(context.session, response)
        return response



    u"""-----------------------------
        ::pkg:: Shimehari.app
        dispatchRequest
        ~~~~~~~~~~~~~~~
        リクエストだす
        [args]
        :request
            リクエスト

        [return]
        :response
            レスポンス
    ------------------------------"""
    def dispatchRequest(self):
        self.tryTriggerBeforeFirstRequest()
        try:
            rv = self.preprocessRequest()
            if rv is None:
                req = _requestContextStack.top.request
                if req.routingException is not None:
                    self.raiseRoutingException(req)
                rule = req.urlRule
                rv = self.controllers[rule.endpoint](**req.viewArgs)
        except Exception, e:
            rv = self.makeResponse(self.handleUserException(e))

        response = self.makeResponse(rv)
        response = self.processResponse(response)
        
        return response



    u"""-----------------------------
        ::pkg:: Shimehari.app
        makeResponse
        ~~~~~~~~~~~~
        レスポンスを生成して返します。
        [args]
        :rv
            リクエスト
        [return]
        :rv
            レスポンス
    ------------------------------"""
    def makeResponse(self, rv):
        status = headers = None

        if isinstance(rv,tuple):
            rv, status, headers = rv + (None,) * (3-len(rv))

        if rv is None:
            raise ValueError('view function does not return a response.')

        if not isinstance(rv, self.responseClass):
            if isinstance(rv, basestring):
                rv = self.responseClass(rv, headers=headers, status=status)
                headers = status = None
            else:
                rv = self.responseClass.force_type(rv,request.environ)
        if status is not None:
            if isinstance(status, basestring):
                rv.status = status
            else:
                rv.status_code = status
        if headers:
            rv.headers.extend(headers)
        return rv



    u"""-----------------------------
        ::pkg:: Shimehari.app
        handleException
        ~~~~~~~~~~~~~~~
        エラーをハンドリングします。

        [args]
        :e
            エラー内容
        [return]

    ------------------------------"""
    def handleException(self, e):

        excType, excValue, excTb = sys.exc_info()
        handler = self.errorHandlerSpec[None].get(500)

        if self.propagateExceptions:
            if excValue is e:
                raise excType, excValue, excTb
            else:
                raise e

        self.logException((excType,excValue,excTb))
        if handler is None:
            return InternalServerError()
        return handler(e)



    def handleHTTPException(self, e):
        handler = self.errorHandlerSpec[None].get(e.code)
        if handler is None:
            return e
        return handler(e)


    def trapHTTPException(self, e):
        if self.config['TRAP_HTTP_EXCEPTIONS']:
            return True
        if self.config['TRAP_BAD_REQUEST_ERRORS']:
            return isinstance(e, BadRequest)
        return False

    def handleUserException(self,e):
        excType, excValue, tb = sys.exc_info()
        assert excValue is e
        
        if isinstance(e, HTTPException) and not self.trapHTTPException(e):
            return self.handleHTTPException(e)

        appHandlers = self.errorHandlerSpec[None].get(None, ())
        for typecheck, handler in appHandlers:
            if isinstance(e, typecheck):
                return handler(e)
        raise excType, excValue, tb


    def raiseRoutingException(self, request):
        if not self.debug or not isinstance(request.routingException, RequestRedirect) \
           or request.method in ('GET', 'HEAD', 'OPTIONS'):
            raise request.routingException



    def testRequestContext(self, *args, **kwargs):
        from shimehari.testing import makeTestEnvironBuilder
        builder = makeTestEnvironBuilder(self, *args, **kwargs)
        try:
            return self.requestContext(builder.get_environ())
        finally:
            builder.close()

    def handleBuildError(self, error, endpoint, **kwargs):
        if self.buildErrorHandlers is None:
            excType, excValue, tb = sys.exc_info()
            if excValue is error :
                raise excType, excValue, tb
            else:
                raise error
        return self.buildErrorHandlers(error, endpoint, **kwargs)




    u"""-----------------------------
        ::pkg:: Shimehari.app
        wsgiApp
        ~~~~~~~

        WSGI アプリとして実行します。(であってるのか)
        [args]
        :environ
            環境変数
        :startResponse
            hoge
    ------------------------------"""
    def wsgiApp(self, environ, startResponse):
        with self.requestContext(environ):
            try:
                response = self.dispatchRequest()
            except Exception, e:
                response = self.makeResponse(self.handleException(e))
            return response(environ, startResponse)
        


    u"""--------------------------------------
        ::pkg:: Shimehari.app
        drink
        ~~~~~    

        アプリを走らせます。
        [args]
        :host
            ホスト名
        :port
            ポート番号
        :debug
            デバッグモードとして起動するかどうか
        :options
            kwargs
    --------------------------------------"""
    def drink(self, host=None, port=None, debug=None, **options):
        from werkzeug.serving import run_simple
        if host is None:
            host = '127.0.0.1'
        if port is None:
            port = 5959
        if debug is not None:
            self.debug = bool(debug)
        options.setdefault('use_reloader', self.debug)
        options.setdefault('use_debugger', self.debug)
        try:
            from werkzeug._internal import _log
            _log('info',' * Shimehari GKGK!')
            run_simple(host, port, self, **options)
        finally:
            self._gotFirstRequest = False



    u"""--------------------------------------
        ::pkg:: Shimenari.app
        run
        ~~~

        アプリを走らせます。
        drink のラッパー。
        WSGI 周りのライブラリとかで
        run を自動的に呼ぶ物対策
    --------------------------------------"""
    def run(self,host=None,port=None, debug=None, **options):
        self.drink(host,port,debug,options)


    def testClient(self, useCookies=True):
        cls = self.testClientCls
        if cls is None:
            from shimehari.testing import ShimehariClient as cls
        return cls(self, self.responseClass, use_cookies=useCookies)



    def __call__(self,environ,startResponse):
        return self.wsgiApp(environ,startResponse)



    def __str__(self):
        return 'Shimehari WSGI Application Framework!'

