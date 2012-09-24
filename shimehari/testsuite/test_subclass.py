#!/usr/bin/env python
# -*- coding: utf-8 -*-


import shimehari
import unittest
from StringIO import StringIO
from logging import StreamHandler
from shimehari.testsuite import ShimehariTestCase
from werkzeug.routing import Rule
from shimehari.configuration import ConfigManager, Config


testConfig = Config('development', {'AUTO_SETUP': False, 'SERVER_NAME': 'localhost', 'PREFERRED_URL_SCHEME': 'https'})
ConfigManager.addConfig(testConfig)


class ShimehariSubclassingTestCase(ShimehariTestCase):
    def testSuperessedExceptionLogging(self):
        class SupressedShimehari(shimehari.Shimehari):
            def logException(self, exc_info):
                pass
        out = StringIO()
        app = SupressedShimehari(__name__)
        app.loggerName = 'shimehariTests/test'
        app.logger.addHandler(StreamHandler(out))

        def index():
            1 / 0

        app.router = shimehari.Router([Rule('/', endpoint='index', methods=['GET'])])
        app.controllers['index'] = index

        rv = app.testClient().get('/')
        self.assertEqual(rv.status_code, 500)
        self.assert_('Internal Server Error' in rv.data)

        err = out.getvalue()
        self.assertEqual(err, '')


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ShimehariSubclassingTestCase))
    return suite
