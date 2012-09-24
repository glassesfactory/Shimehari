#!/usr/bin/env python
# -*- coding: utf-8 -*-

from shimehari.shared import _requestContextStack
from shimehari.helpers import lockedCachedProperty
from werkzeug.datastructures import ImmutableDict


def _defaultTemplateCtxProcessor():
    reqctx = _requestContextStack.top
    return dict(
        config=reqctx.app.config,
        request=reqctx.request,
        session=reqctx.session,
        shared=reqctx.shared
    )


def _render(template, context):
    rv = template.render(context)
    return rv


def renderTemplate(templateNameOrList, **context):
    ctx = _requestContextStack.top
    ctx.app.updateTemplateContext(context)
    return _render(ctx.app.templateEnv.get_or_select_template(templateNameOrList),
        context)


def renderTempalteString(source, **context):
    ctx = _requestContextStack.top
    ctx.app.updateTemplateContext(context)
    return _render(ctx.app.templateEnv.from_string(source), context)


u"""
===============================
    ::pkg:: Shimehari.template
    Templater
    ~~~~~~~~~~

    各テンプレートエンジンに共通のインターフェースをもたらす
    アダプターのベーシッククラス

===============================
"""


class AbstractTemplater(object):
    templateOptions = ImmutableDict()

    def __init__(self, app, *args, **options):
        self.app = app

        if 'templateOptions' in options:
            self.templateOptions = options['templateOptions']

    @lockedCachedProperty
    def templateLoader(self):
        raise NotImplementedError()

    def templateEnv(self):
        raise NotImplementedError()

    def createTemplateEnvironment(self):
        raise NotImplementedError()

    def dispatchLoader(self, app):
        raise NotImplementedError()

    def updateTemplateContext(self, context):
        funcs = self.app.templateContextProcessors[None]
        org = context.copy()
        for func in funcs:
            context.update(func())
        context.update(org)
