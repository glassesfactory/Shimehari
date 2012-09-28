#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import shimehari
from shimehari.routing import *
from shimehari.testsuite import ShimehariTestCase
from shimehari.configuration import ConfigManager, Config
from shimehari.testsuite.testApp.controllers import IndexController, ChildController

testConfig = Config('development', {'AUTO_SETUP': False, 'SERVER_NAME': 'localhost', 'PREFERRED_URL_SCHEME': 'https', 'CONTROLLER_AUTO_NAMESPACE': False})


class testResource(ShimehariTestCase):
    def testMakeResource(self):
        self.assertNotEqual(Resource(IndexController), Exception)

        def index(*args, **kwargs):
            return 'index'

        def show(*args, **kwargs):
            return 'show'
        rule = RESTfulRule('hoge', index=index, show=show)
        self.assertNotEqual(Resource(rule), Exception)
        self.assertRaises(ValueError, Resource, 1)

    def testExceptsAndOnly(self):
        self.assertRaises(ValueError, Resource, IndexController, excepts=['show'], only=['show'])

    def testMakeResourceWithChildren(self):
        res = Resource(ChildController)
        self.assertNotEqual(Resource(IndexController, children=[res]), Exception)

    def testAdd(self):
        res = Resource()
        self.assertNotEqual(res.add(IndexController), Exception)
        self.assertRaises(ValueError, res.add, 'puuuu')

    def testAddRule(self):
        res = Resource(IndexController)

        def testUserID(*args, **kwargs):
            return userid
        res.addRule('/<userid>', testUserID)

    def testRefresh(self):
        res = Resource(IndexController)
        self.assertNotEqual(res.refresh(), Exception)

    def testGetNameFromRESTAction(self):
        res = Resource()
        self.assertEqual(res.getNameFromRESTAction('megane', 'show'), '/megane/<int:id>')
        self.assertEqual(res.getNameFromRESTAction('megane', 'index', root=True), '/')
        self.assertRaises(ValueError, res.getNameFromRESTAction, 'megane', 'ninja')


class testRESTfulRule(ShimehariTestCase):
    def testMakeRESTfulRule(self):
        def index(*args, **kwargs):
            return 'index'

        def show(*args, **kwargs):
            return 'show'

        def edit(*args, **kwargs):
            return 'edit'

        def new(*args, **kwargs):
            return 'new'

        def create(*args, **kwargs):
            return 'create'

        def update(*args, **kwargs):
            return 'update'

        def destroy(*args, **kwargs):
            return 'destroy'

        rule = RESTfulRule('test', index, show, edit, new, create, update, destroy)

        self.assertNotEqual(rule._rules, [])
        self.assertNotEqual(len(rule._rules), 0)

    def testRefresh(self):
        def index(*args, **kwargs):
            return 'index'

        rule = RESTfulRule('test', index)
        self.assertNotEqual(rule.refresh(), Exception)


class testRESTfulRouter(ShimehariTestCase):
    def testBeInstanseRouter(self):
        self.assertNotEqual(RESTfulRouter([Resource(IndexController)]), TypeError)

        def index(*args, **kwargs):
            return 'index'

        def show(*args, **kwargs):
            return 'show'
        self.assertNotEqual(RESTfulRouter([RESTfulRule('test', index, show)]), Exception)

        router = RESTfulRouter([
            Resource(IndexController),
            RESTfulRule('test', index, show),
        ])

        self.assertNotEqual(router, Exception)

        self.assertRaises(TypeError, RESTfulRouter, [1, 2, 3])

    def testHasChild(self):
        ConfigManager.removeConfig('development')
        ConfigManager.addConfig(testConfig)

        def index(*args, **kwargs):
            return 'index'

        def show(*args, **kwargs):
            return 'show'
        router = RESTfulRouter([
            Resource(IndexController, [Resource(ChildController)]),
            RESTfulRule('test', index, show),
        ])

        app = shimehari.Shimehari(__name__)
        app.setupTemplater()
        app.router = router
        app.setControllerFromRouter(router)
        c = app.testClient()
        rv = c.get('/index/1', content_type='text/planetext')
        self.assertEqual(rv.data, "response show")

    def testDump(self):
        router = RESTfulRouter([Resource(IndexController)])
        self.assertEqual(isinstance(router.dump(), basestring), True)
