#!/usr/bin/env python
# -*- coding: utf-8 -*-

class ShimehariException(Exception):
    def __init__(self, description):
        self.description = description

    def __str__(self):
        return 'ShimehariError: %s' % self.description



class ShimehariHTTPError(ShimehariException):
    def __init__(self,description, host='127.0.0.1', port=5959):
        ShimehariException.__init__(description)



class ShimehariSetupError(ShimehariException):
    def __str__(self):
        return 'ShimehariSetupError: %s' % self.description


class CommandError(Exception):pass
    

class DrinkError(Exception):
    def __init__(self, description, host=None, port=None):
        self.description = description
        self.host = host
        self.port = port

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return 'Shimehari Drink Command is Error: %s\n host=%s\n port=%d' % (self.description, self.host, self.port)

from werkzeug.exceptions import HTTPException, BadRequest
from shimehari.helpers import json
class JSONHTTPExceptions(HTTPException):
    def get_body(self,environ):
        return json.dumps(dict(description=self.get_description(environ)))

    def get_headers(self, environ):
        return [('Content-Type','application/json')]

class JSONBadRequest(JSONHTTPExceptions, BadRequest):
    description = ('ブラウザ、もしくはプロクシが送ったリクエストを、このアプリケーションでは処理できません。')