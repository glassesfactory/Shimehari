#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
===============================
    Shimehari.routing
    ~~~~~~~~~~~~~~~~~
    ルーティング周り
===============================
"""
import re, sys
from werkzeug.routing import Map, Rule, RuleTemplate

from shimehari.controllers import AbstractController
from shimehari.core import (RESTFUL_ACTIONS, ALLOWED_HTTP_METHOD_NAMES, RESTFUL_METHODS_MAP,
                            importFromString)
from shimehari.helpers import getHandlerAction, fillSpace
from shimehari.configuration import ConfigManager, Config


u"""
===============================
    Shimehari.routing.AbstractRouter
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ルーター
===============================
"""
class AbstractRouter(Map):
    def __init__(self,rules=[], defaultSubdomain='', charset='utf-8',
                strict_slashes=True, redirectDefaults=True,
                converters=None, sortParameters=False, sortKey=None,
                encodingErrors='replace', hostMatching=False):

        Map.__init__(self, rules=rules,default_subdomain=defaultSubdomain, charset=charset,
                    strict_slashes=strict_slashes, redirect_defaults=redirectDefaults,
                    converters=converters, sort_parameters=sortParameters, sort_key=sortKey,
                    encoding_errors=encodingErrors, host_matching=hostMatching)

        self._rules = []

        for rule in rules:
            self.add(rule)


    u"""-----------------------------
        Shimehari.AbstractRouter.dump
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        現在定義されているルーティングを出力します。
        [return]
            :str 定義されているルーティング
    ------------------------------"""
    def dump(self):
        _map = ''
        for rule in self._rules:
            method = list(rule.methods.copy())
            if 'HEAD' in method:
                method.remove('HEAD')
            _map += fillSpace(','.join(method), 15)
            _map += fillSpace(unicode(rule).encode('utf-8') + '  ', 50)
            _map += '[action => '
            _map += rule.endpoint.__name__
            clsName = rule.endpoint.im_class.__name__
            _map +=  ', controller => ' + clsName + ']\n'
        return _map


u"""
===============================
    Shimehari.routing.RESTfulRouter
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    リソースを指定して自動的にルーティング生成

    Constructor

    :resources
        ルーティングを登録したいリソース。
            => Shimehari.routing.Resource

    :defaultSubdomain
        prefix として指定するサブドメインを設定します。

    :charset
        文字コードを設定します。

    :strictSlashes
        ほげほげ

    :redirectDefaults
        ほげほげ

    :converters
        こんばーたーをしてい

    :sortParameters
        ほげほげ

    :sortKey
        ふがふが

    :encordingErrors
        ほげほげ

    :hostMatching
        ああああ

===============================
"""
class RESTfulRouter(AbstractRouter):
    def __init__(self, resources=[], defaultSubdomain='', charset='utf-8',
                strict_slashes=True, redirectDefaults=True,
                converters=None, sortParameters=False, sortKey=None,
                encodingErrors='replace', hostMatching=False):

        AbstractRouter.__init__(self, rules=[],defaultSubdomain=defaultSubdomain, charset=charset,
                    strict_slashes=strict_slashes, redirectDefaults=redirectDefaults,
                    converters=converters, sortParameters=sortParameters, sortKey=sortKey,
                    encodingErrors=encodingErrors, hostMatching=hostMatching)

        self._rules = []

        for resource in resources:
            rules = []
            if isinstance(resource, (Resource, RESTfulRule):
                for rule in resource._rules:
                    self.add(rule)
            elif isinstance(resource, list):
                for rule in resource:
                    self.add(rule)
            elif isinstance(resource, (Rule, Root)):
                self.add(resource)
            else:
                raise TypeError('resources rule is invalid.')



class Root(Rule):
    root = True
    def __init__(self, endpoint, methods=['get']):
        Rule.__init__(self, '/', endpoint=endpoint, methods=methods)



u"""
===============================

    Shimehari.routing.RESTfulRule
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    CRUD 準拠 URL ルール
    こういうのはどうだろう…
    :index
        index
    :show
        show
    :edit
        edit

===============================
"""

class RESTfulRule(object):

    parent = None

    baseName = None

    def __init__(self, name, index=None, show=None, edit=None, new=None, create=None, update=None, destroy=None, methods=[]):
        self.baseName = name
        self.getName = self.getNameFromRESTAction

        rules = []

        if index is not None:
            rules.append(Rule(self.getName(name, 'index'), endpoint=index, methods=['get']))
        if show is not None:
            rules.append(Rule(self.getName(name, 'show'), endpoint=show, methods=['get','post']))
        if edit is not None:
            rules.append(Rule(self.getName(name, 'edit'), endpoint=edit, methods=['get','post']))
        if new is not None:
            rules.append(Rule(self.getName(name, 'new'), endpoint=new, methods=['get']))
        if create is not None:
            rules.append(Rule(self.getName(name, 'create'), endpoint=create, methods=['post']))
        if update is not None:
            rules.append(Rule(self.getName(name, 'update'), endpoint=update, methods=['put']))
        if destroy is not None:
            rules.append(Rule(self.getName(name, 'destroy'), endpoint=destroy, methods=['delete']))
        self._rules = rules


    def refresh(self):
        for rule in self._rules:
            if self.parent:
                rule.rule = self.parent.baseName + '/' + rule.rule
            # rule.refresh()


    #uアクション名から URL Name を生成します
    def getNameFromRESTAction(self, name, action, root=False):
        if not name.startswith('/') and len(name) > 1:
            name = '/' + name
        if name.endswith('/') and len(name) > 1:
            name = name[:len(name)-1]

        if root:
            name = ''

        _act = action.lower()
        if _act == 'index' or _act == 'create':
            if name == '' and root:
                return '/'
            return name
        elif _act == 'show' or _act == 'update' or _act == 'destroy':
            return name + '/<int:id>'
        elif _act == 'edit':
            return name + '/<int:id>/edit'
        elif _act == 'new':
            return name + '/new'
        else:
            raise ValueError('RESTfulRule')


u"""
===============================
    Shimehari.routing.Resource
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    リソース
    [args]
    :controller
        type::AbstractController or Dictionary
        リソースとして指定するコントローラー


===============================
"""
class Resource(Map):

    u"""親"""
    parent = None

    u"""名前"""
    baseName = None

    orgName = None


    def __init__(self, controller=None, children=[], name=None, only=[], excepts=[], root=False, 
                subdomain=None, buildOnly=False, strict_slashes=None, redirectTo=None,
                alias=False, host=None, defaults=None, namespace=None):
      
        Map.__init__(self, rules=[], default_subdomain='', charset='utf-8',
                 strict_slashes=True, redirect_defaults=True,
                 converters=None, sort_parameters=False, sort_key=None,
                 encoding_errors='replace', host_matching=False)

        if only != [] and excepts != []:
                raise ValueError('allow or deny!!!!')

        self._rules = []

        self.children = children

        self.only = only

        self.excepts = excepts

        self.root = root

        self.subdomain = self.default_subdomain = subdomain

        self.buildOnly = buildOnly

        self.strict_slashes = strict_slashes

        self.redirectTo = redirectTo

        self.alias = alias

        self.host = host

        self.defaults = defaults

        self.name = name

        self.getName = self.getNameFromRESTAction

        self.namespace = namespace
        if self.namespace:
            if self.namespace.startswith('/'):
                self.namespace = self.namespace[1:]
            if self.namespace.endswith('/'):
                self.namespace = self.namespace[:len(self.namespace)-1]
        #ディレクトリが深かった時自動で
        elif controller is not None: 
            config = ConfigManager.getConfig()
            if config['CONTROLLER_AUTO_NAMESPACE']:
                package = controller.__module__.split('.')
                appFolder = config['APP_DIRECTORY']
                controllerFolder = config['CONTROLLER_DIRECTORY']
                package.remove(appFolder)
                package.remove(controllerFolder)

                self.orgName = package[len(package)-1]
                package = package[:len(package)-1]
                self.namespace = "/".join(package)
            
        if controller:
            controller = self._checkControllerType(controller)
            if not name:
                self.baseName = self.orgName = controller.baseName
            self.add(controller)

        #uuuumu
        if self.root:
            self.baseName = '/'

        if self.parent:
            self.baseName = self.parent.baseName + '/' + self.baseName

        if isinstance(self.children, dict) and len(self.children) > 0:
            for child in self.children:
                if not isinstance(child, Resource) and not isinstance(child, RESTfulRule) and not isinstance(child, Rule):
                    raise TypeError('children is invalid')
                if isinstance(child, Rule):
                    child.rule = self.baseName + '/' + child.rule
                else:
                    child.parent = self
                child.refresh()
                if isinstance(child, Resource):
                    self._rules = self._rules + child._rules


    def _checkControllerType(self, controller):
        from shimehari.controllers import AbstractController
        if isinstance(controller, str):
            controller = importFromString(controller)

        import inspect
        if inspect.isclass(controller):
            controller = controller(controller.__name__)
        if not isinstance(controller, AbstractController) and \
           not isinstance(controller, RESTfulRule):
            if isinstance(controller, dict):
                for rule in dict:
                    if not isinstance(rule, Rule):
                        raise ValueError('controller failed:: rule is invalid')
                        sys.exit()
            else:
                raise ValueError('controller is invalid... \n target instansce type is  %s' % type(controller))
        return controller

    #みなおし
    u"""----------------------------------------

        [private]
        ::pkg:: Shimehari.routing
        _addRuleFromController
        ~~~~~~~~~~~~~~~~~~~~~~
        渡されたコントローラーから URL ルールを生成、追加します。

        [args]
            :controller ルールを追加したいコントローラー

    ---------------------------------------------"""
    def _addRuleFromController(self, controller):
        actions = RESTFUL_ACTIONS.copy()
        if self.only is not None:
            actions = RESTFUL_ACTIONS.intersection(self.only)
        if self.excepts is not None:    
            actions = RESTFUL_ACTIONS.difference(self.excepts)

        for action in actions:
            handler = getHandlerAction(controller, action)
            if handler is not None:
                name = self.getName(self.baseName, action, self.root)

                methods = RESTFUL_METHODS_MAP[action.lower()]
                rule = Rule(name, defaults=self.defaults, endpoint=handler, 
                            subdomain=self.subdomain, methods=methods, build_only=self.buildOnly,
                            strict_slashes=self.strict_slashes, redirect_to=self.redirectTo, alias=self.alias, host=self.host)

                self._rules.append(rule)



    u"""----------------------------------------

        _addRuleFromRules
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        Rule が格納されたディクショナリをルールに追加します。

        [args]
            :rules 追加したい Rule を格納したディクショナリ

    ---------------------------------------------"""
    def _addRuleFromRules(self, rules):
        for rule in rules:
            if not isinstance(rule, RuleBase):
                raise TypeError('Rule type is invalid')
            self._rules.append(rule)


    #aaaaa
    u"""----------------------------------------

        add
        ~~~
        
        コントローラー、もしくはルールを追加します。
        [args]
            :controller 
                ルールを追加したいコントローラー、もしくは
                RESTfulRule、ルールを格納したディクショナリ

    ---------------------------------------------"""
    def add(self,controller):
        import inspect
        if inspect.isclass(controller):
            controller = controller(controller.__name__)
            self.baseName = controller.baseName
        if isinstance(controller, AbstractController):
            self._addRuleFromController(controller)
        elif isinstance(controller, RESTfulRule):
            self._rules = controller._rules
        elif isinstance(controller, dict):
            self._addRuleFromRules(controller)
        else:
            raise ValueError('out!')


    def refresh(self):
        for rule in self._rules:
            if self.parent:
                rule.rule = '/' + self.parent.baseName + rule.rule



    def addRule(self, name, handler, methods=[], *args, **kwargs):
        rule = Rule(name, defaults=self.defaults, endpoint=handler, 
                            subdomain=self.subdomain, methods=methods, build_only=self.buildOnly,
                            strict_slashes=self.strict_slashes, redirect_to=self.redirectTo, alias=self.alias, host=self.host)
        self._rules.append(rule)
        self.refresh()
        return self

    #上書きできるようにしよう
    def overRideRule(self, action, name, handler=None, methods=[], *args, **kwargs):
        print self._rules


    u"""アクション名から URL Name を生成します"""
    def getNameFromRESTAction(self, name, action, root=False):
        if self.namespace:
            name = self.namespace + '/' + name

        if not name.startswith('/') and len(name) > 1:
            name = '/' + name
        if name.endswith('/') and len(name) > 1:
            name = name[:len(name)-1]

        if root:
            name = '' 

        _act = action.lower()
        if _act == 'index' or _act == 'create':
            if name == '' and root:
                return '/'
            return name
        elif _act == 'show' or _act == 'update' or _act == 'destroy':
            return name + '/<int:id>'
        elif _act == 'edit':
            return name + '/<int:id>/edit'
        elif _act == 'new':
            return name + '/new'
        else:
            raise ValueError('RESTfulRule')


u"""
werkzeug の中に似たのがあるっぽい…
"""
class Group(object):
    def __init__(self, name, children):
        for child in children:
            if isinstance(child, Resource):
                pass
                child.namespace = name
                child.refresh()
            elif isinstance(child, Rule):
                child.rule = name + '/' + child.name
                child.refresh()
            else:
                raise RuntimeError('settei dekimasen.')




#defaultRouterClass
Router = RESTfulRouter