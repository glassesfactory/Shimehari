#!/usr/bin/env python
# -*- coding: utf-8 -*-


from werkzeug.exceptions import abort
from werkzeug.utils import redirect

from .app import Shimehari
from .controllers import ApplicationController
from .configuration import ConfigManager
from .logging import createLogger
from .helpers import jsonAvailable, json, urlFor, jsonify, sendFile, flash, getFlashedMessage
from .routing import Router, Resource, RESTfulRule, Root, Group
from .shared import request, session, shared, _requestContextStack, _appContextStack, currentApp
from .template import renderTemplate, renderTempalteString
from .wrappers import Request, Response
from .cache import Cache

VERSION = '0.1.8'
AUTHOR = 'Yamaguchi Eikichi, Keiichiro Matsumoto'


def getVersion():
    return VERSION
