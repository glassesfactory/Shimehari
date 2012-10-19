#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
===============================
    Shimehari.wrappers
    ~~~~~~~~~~~~~~~~~~
    リクエストやらレスポンスやら

===============================
"""

from werkzeug.utils import cached_property
from werkzeug.wrappers import Request as RequestBase, Response as ResponseBase
from shimehari.core.helpers import attachEnctypeErrorMultidict
from shimehari.core.exceptions import JSONBadRequest
from shimehari.helpers import _assertHaveJson, json
from shimehari.shared import _requestContextStack


class Request(RequestBase):
    urlRule = None
    viewArgs = None

    routingException = None

    @property
    def endpoint(self):
        if self.urlRule is not None:
            return self.urlRule.endpoint

    @cached_property
    def json(self):
        if __debug__:
            _assertHaveJson()
        if self.mimetype == 'application/json':
            reqCharset = self.mimetype_params.get('charset')
            try:
                if reqCharset is not None:
                    return json.loads(self.data, encoding=reqCharset)
                return json.loads(self.data)
            except ValueError, error:
                return self.jsonLoadFailedHandler(error)

    def jsonLoadFailedHandler(self, error):
        raise JSONBadRequest()

    def _load_from_data(self):
        RequestBase._load_from_data(self)

        context = _requestContextStack.top

        if context is not None and context.app.debug \
           and self.mimetype != 'multipart/form-data' and not self.files:
            attachEnctypeErrorMultidict(self)


class Response(ResponseBase):
    default_mimetype = 'text/html'
