#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import shimehari
import time
from shimehari.cache import Cache
from shimehari.core.cachestore import NullCacheStore, SimpleCacheStore
from shimehari.testsuite import ShimehariTestCase
from shimehari.testsuite.testApp.controllers import IndexController, ChildController

class TestCache(ShimehariTestCase):
    def testCacheGetterSetter(self):
        cache = Cache(storetype='simple')
        cache.set('sake', 'shimehari')
        rv = cache.get('sake')
        self.assertEqual(rv, 'shimehari')
        self.assert_(cache.get('osake') is None)

    def testCacheGetAndSetMany(self):
        cache = Cache(storetype='simple')
        cache.setMany({'sake':'shimehari', 'osake':'kagetora'})
        rv = cache.get('sake')
        self.assertEqual(rv, 'shimehari')
        rv = cache.get('osake')
        self.assertEqual(rv, 'kagetora')
        rv = cache.getMany('sake', 'osake')
        self.assertEqual(rv, ['shimehari', 'kagetora'])
        rv = cache.getDict('sake', 'osake')
        self.assertEqual(rv, {'sake':'shimehari', 'osake':'kagetora'})

    def testCacheDelete(self):
        cache = Cache(storetype='simple')
        cache.set('sake','shimehari')
        rv = cache.get('sake')
        self.assertEqual(rv,'shimehari')
        cache.delete('sake')
        rv = cache.get('sake')
        self.assert_(rv is None)

        cache.setMany({'sake':'shimehari', 'osake':'kagetora'})
        rv = cache.getMany('sake', 'osake')
        self.assertEqual(rv, ['shimehari', 'kagetora'])
        cache.deleteMany('sake','osake')
        rv = cache.get('sake')
        self.assert_(rv is None)
        rv = cache.get('osake')
        self.assert_(rv is None)

    def testCacheAdd(self):
        cache = Cache('simple')
        rv = cache.get('sake')
        self.assert_(rv is None)
        cache.add('sake', 'shimehari')
        self.assertEqual(cache.get('sake'), 'shimehari')
        cache.add('sake', 'kagetora')
        self.assertNotEqual(cache.get('sake'), 'kagetora')
        cache.set('sake', 'kagetora')
        self.assertEqual(cache.get('sake'), 'kagetora')

    def testCacheClear(self):
        cache = Cache('simple')
        d = {}
        [d.setdefault(str(x),x) for x in range(100)]
        cache.setMany(d)
        keys = [str(x) for x in range(100)]
        self.assertNotIn(None,cache.getMany(*keys))
        cache.clear()
        self.assertIn(None,cache.getMany(*keys))

    def testSetCacheStore(self):
        cache = Cache()
        self.assertIsInstance(cache.store, NullCacheStore)
        cache.setCacheStore(SimpleCacheStore())
        self.assertIsInstance(cache.store, SimpleCacheStore)

    def testCacheLimit(self):
        cache = Cache(storetype='simple')
        cache.set('sake', 'shimehari' ,timeout=10)
        self.assertEqual(cache.get('sake'), 'shimehari')
        time.sleep(11)
        self.assert_(cache.get('sake') is None)





