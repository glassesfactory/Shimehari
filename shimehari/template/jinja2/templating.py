#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import posixpath
from jinja2 import BaseLoader, Environment as BaseEnvironment, TemplateNotFound, FileSystemLoader
from shimehari.helpers import lockedCachedProperty
from shimehari.template import AbstractTemplater
from shimehari.helpers import urlFor, _toJsonFilter
from shimehari.crypt import generateCSRFToken


class Environment(BaseEnvironment):
    def __init__(self, app, *args, **options):
        if 'loader' not in options:
            options['loader'] = app.createGlobalTemplateLoader()

        BaseEnvironment.__init__(self, *args, **options)
        self.app = app


class DispatchJinjaLoader(BaseLoader):
    def __init__(self, app):
        self.app = app

    def get_source(self, environment, template):
        for loader, localName in self._iterLoaders(template):
            try:
                return loader.get_source(environment, localName)
            except TemplateNotFound:
                pass
        raise TemplateNotFound(template)

    def _iterLoaders(self, template):
        loader = self.app.templateLoader
        if loader is not None:
            yield loader, template

    def listTemplates(self):
        result = set()
        loader = self.app.templateLoader
        if loader is not None:
            result.update(loader.list_templates())
        return list(result)


class Jinja2Templater(AbstractTemplater):
    def __init__(self, app, *args, **options):
        AbstractTemplater.__init__(self, app, *args, **options)

    @lockedCachedProperty
    def templateLoader(self):
        if self.app.viewFolder is not None:
            return FileSystemLoader(os.path.join(self.app.rootPath, self.app.appFolder, self.app.viewFolder))

    def templateEnv(self):
        rv = self.createTemplateEnvironment()
        return rv

    def createTemplateEnvironment(self):
        options = self.templateOptions

        if 'autoescape' in options:
            options['autoescape'] = self.selectJinjaAutoescape

        rv = Environment(self.app, **options)
        #いるかなー
        rv.globals.update(
            url_for=urlFor,
            csrfToken=generateCSRFToken
        )
        rv.filters['tojson'] = _toJsonFilter
        return rv

    def dispatchLoader(self, app):
        return DispatchJinjaLoader(app)

templater = Jinja2Templater
