#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import shimehari
from shimehari.routing import Resource
from shimehari.configuration import ConfigManager, Config
from shimehari.testsuite import ShimehariTestCase
from shimehari.testsuite.testApp.controllers import IndexController
from werkzeug.routing import Rule, Map


testConfig = Config('development', {'AUTO_SETUP': False, 'SERVER_NAME': 'localhost', 'PREFERRED_URL_SCHEME': 'https'})


class TestAppContext(ShimehariTestCase):
    def testGenerateURL(self):
        ConfigManager.addConfig(testConfig)
        app = shimehari.Shimehari(__name__)

        def index(*args, **kwargs):
            return 'index'
        app.router = shimehari.Router([Rule('/', endpoint='index', methods=['GET'])])

        with app.appContext():
            rv = shimehari.urlFor('index')
            self.assertEqual(rv, 'https://localhost/')

    def testRaiseErrorGenerateURLRequireServerName(self):
        app = shimehari.Shimehari(__name__)
        app.config['SERVER_NAME'] = None
        with app.appContext():
            with self.assertRaises(RuntimeError):
                shimehari.urlFor('index')

    def testRaiseErrorWithoutContext(self):
        with self.assertRaises(RuntimeError):
            shimehari.urlFor('index')

    def testRequestContextMeansAppContext(self):
        ConfigManager.addConfig(testConfig)
        app = shimehari.Shimehari(__name__)
        with app.testRequestContext():
            self.assertEqual(shimehari.currentApp._get_current_object(), app)
        self.assertEqual(shimehari._appContextStack.top, None)

    def testAppContextProvidesCurrentApp(self):
        ConfigManager.addConfig(testConfig)
        app = shimehari.Shimehari(__name__)
        with app.appContext():
            self.assertEqual(shimehari.currentApp._get_current_object(), app)
        self.assertEqual(shimehari._appContextStack.top, None)

    def testAppTearingDown(self):
        cleanStuff = []
        app = shimehari.Shimehari(__name__)

        @app.tearDownAppContext
        def cleanup(exception):
            cleanStuff.append(exception)

        with app.appContext():
            pass
        self.assertEqual(cleanStuff, [])

    def testCustomRequestGlobalsClass(self):
        class CustomRequestGlobals(object):
            def __init__(self):
                self.spam = 'sakerin'
        app = shimehari.Shimehari(__name__)
        app.setupTemplater()
        app.sharedRequestClass = CustomRequestGlobals
        with app.testRequestContext():
            self.assertEqual(shimehari.renderTemplateString('{{ shared.spam }}'), 'sakerin')


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestAppContext))
    return suite
