#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shimehari
import unittest
from werkzeug.routing import Rule
from shimehari.testsuite import ShimehariTestCase
from shimehari.configuration import ConfigManager, Config
from shimehari.routing import Router, Resource
from shimehari.controllers import ApplicationController


testConfig = Config('development', {'AUTO_SETUP': False, 'SERVER_NAME': 'localhost', 'PREFERRED_URL_SCHEME': 'https'})


class TestController(ApplicationController):
    def index(self, *args, **kwargs):
        return 'Shimehari nomitai.'


class ShimehariAppTestCase(ShimehariTestCase):
    def testGotFirstRequest(self):
        ConfigManager.addConfig(testConfig)
        app = shimehari.Shimehari(__name__)
        self.assertEqual(app.gotFirstRequest, False)

        def returnHello(*args, **kwargs):
            return 'Hello'
        app.router = shimehari.Router([Rule('/hell', endpoint='returnHello', methods=['POST'])])
        app.controllers['returnHello'] = returnHello
        c = app.testClient()
        c.get('/hell', content_type='text/planetext')
        self.assert_(app.gotFirstRequest)

    #u---mu
    def testLogger(self):
        ConfigManager.addConfig(testConfig)
        app = shimehari.Shimehari(__name__)
        self.assert_(type(app.logger))

    def testGetConfig(self):
        ConfigManager.addConfig(testConfig)
        app = shimehari.Shimehari(__name__)
        self.assertEqual(app.getConfig(), testConfig)

    def testSetControllerFromRouter(self):
        ConfigManager.addConfig(testConfig)
        app = shimehari.Shimehari(__name__)
        self.assertEqual(app.controllers, {})
        router = Router([Resource(TestController, root=True)])
        app.setControllerFromRouter(router)
        self.assertNotEqual(app.controllers, {})

    def testAddController(self):
        ConfigManager.addConfig(testConfig)
        app = shimehari.Shimehari(__name__)
        self.assertEqual(app.controllers, {})
        app.addController(TestController)
        self.assertNotEqual(app.controllers, {})

    def testAddRoute(self):
        ConfigManager.addConfig(testConfig)
        app = shimehari.Shimehari(__name__)
        self.assertEqual(app.controllers, {})
        self.assertEqual(app.router._rules, [])

        def index(*args, **kwargs):
            return 'Sake nomitai.'
        app.addRoute('/', index)
        c = app.testClient()
        rv = c.get('/', content_type='text/html')
        self.assertEqual(rv.status_code, 200)
        self.assert_('Sake nomitai.' in rv.data)

    def testSetup(self):
        # ConfigManager.addConfig(testConfig)
        ConfigManager.removeConfig('development')
        ConfigManager.addConfig(Config('development', {'AUTO_SETUP': False, 'SERVER_NAME': 'localhost', 'PREFERRED_URL_SCHEME': 'https'}))
        app = shimehari.Shimehari(__name__)
        app.appPath = os.path.join(app.rootPath, 'testApp')
        app.appFolder = 'shimehari.testsuite.testApp'
        app.setupTemplater()
        app.setupBindController()
        app.setupBindRouter()
        self.assertNotEqual(app.controllers, {})
        self.assertNotEqual(app.router._rules, {})
        pass

    def testTryTriggerBeforeFirstRequest(self):
        ConfigManager.removeConfig('development')
        ConfigManager.addConfig(testConfig)
        app = shimehari.Shimehari(__name__)

        app.testCnt = 0

        @app.beforeFirstRequest
        def doFirst():
            app.testCnt = app.testCnt + 1
            return app.testCnt

        def returnHello(*args, **kwargs):
            return 'Hello'
        app.router = shimehari.Router([Rule('/hell', endpoint='returnHello', methods=['POST'])])
        app.controllers['returnHello'] = returnHello
        c = app.testClient()
        self.assertEqual(app.testCnt, 0)
        c.get('/hell', content_type='text/planetext')
        self.assertEqual(app.testCnt, 1)
        c.get('/hell', content_type='text/planetext')
        self.assertEqual(app.testCnt, 1)

    def testPreprocessRequest(self):
        ConfigManager.removeConfig('development')
        ConfigManager.addConfig(testConfig)
        app = shimehari.Shimehari(__name__)

        app.testCnt = 0

        @app.beforeRequest
        def doRequest():
            app.testCnt = app.testCnt + 1
            return app.testCnt

        def returnHello(*args, **kwargs):
            return 'Hello'
        app.router = shimehari.Router([Rule('/hell', endpoint='returnHello', methods=['POST'])])
        app.controllers['returnHello'] = returnHello
        c = app.testClient()
        self.assertEqual(app.testCnt, 0)
        c.get('/hell', content_type='text/planetext')
        self.assertEqual(app.testCnt, 1)
        c.get('/hell', content_type='text/planetext')
        self.assertEqual(app.testCnt, 2)

    def testProcessResponse(self):
        ConfigManager.removeConfig('development')
        ConfigManager.addConfig(testConfig)
        app = shimehari.Shimehari(__name__)

        app.testCnt = 0

        @app.afterRequest
        def doRequest(res):
            app.testCnt = app.testCnt + 1
            return res

        def returnHello(*args, **kwargs):
            return 'Hello'
        app.router = shimehari.Router([Rule('/hell', endpoint='returnHello', methods=['POST'])])
        app.controllers['returnHello'] = returnHello
        c = app.testClient()
        self.assertEqual(app.testCnt, 0)
        c.get('/hell', content_type='text/planetext')
        self.assertEqual(app.testCnt, 1)
        c.get('/hell', content_type='text/planetext')
        self.assertEqual(app.testCnt, 2)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ShimehariAppTestCase))
    return suite
