#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
===============================
    Shimehari.controllers
    ~~~~~~~~~~~~~~~~~~~~~
    コントローラーたち
===============================
"""
from abc import ABCMeta, abstractmethod

u"""
===============================
    Shimehari.controllers.AbstractController
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    コントローラーの抽象クラス
===============================
"""


class AbstractController(object):

    __metaclass__ = ABCMeta

    baseName = ''

    folderPrefix = ''

    def __init__(self, name):
        if not name:
            name = self.__class__.__name__
        self.name = name
        if 'Controller' in name:
            name = name.replace('Controller', '')

        self.baseName = name.lower()

    @abstractmethod
    def httpMethodNotAllowed(self, templateName='405.html'):
        return

    def bindHelper(self, helperName=None):
        pass


u"""
===============================
    Shimehari.controllers.TemplateRenderableMixIn
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    テンプレートレンダラブルみっくすいん
===============================
"""


class TemplateRenderableMixIn(object):

    def renderToResponse(self, context, **resKwargs):

        return

    def getTemplateName(self):
        if self.templateName is None:
            raise  # なんちゃかえらー
        else:
            return self.templateName


from shimehari.template import renderTemplate

u"""
===============================
    Shimehari.controllers.ApplicationController
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    コントローラーの具象クラス
===============================
"""


class ApplicationController(TemplateRenderableMixIn, AbstractController):

    _cache = None

    def cache():
        "The cache property."
        def fget(self):
            return self._cache

        #setter 塞ぐか
        def fset(self, value):
            self._cache = value

        def fdel(self):
            del self._cache
        return locals()
    cache = property(**cache())

    def __init__(self, name):
        AbstractController.__init__(self, name)

    def renderTemplate(self, templateName):
        return renderTemplate(templateName)

    def httpMethodNotAllowed(self, templateName='405.html'):
        pass
