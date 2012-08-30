#!/usr/bin/env python
# -*- cofing: utf-8 -*-


from werkzeug.exceptions import abort
from werkzeug.utils import redirect

from .app import Shimehari
from .controllers import ApplicationController
from .helpers import jsonAvailable, json, urlFor, jsonify, sendFile
from .routing import Router, Resource, RESTfulRule
from .shared import request, session, shared, _requestContextStack, _appContextStack, currentApp
from .template import renderTemplate, renderTempalteString
from .wrappers import Request, Response

VERSION = '0.1.4'
AUTHOR = 'Yamaguchi Eikichi, Keiichiro Matsumoto'


def getVersion():
    return VERSION