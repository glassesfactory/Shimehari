#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
===============================
    Shimehari.testsuite
    ~~~~~~~~~~~~~~~~~~~
    テスト
===============================
"""

import os, sys
import unittest
import warnings
from StringIO import StringIO
from contextlib import contextmanager
from werkzeug.utils import import_string, find_modules
import shimehari


def addToPath(path):
    if not os.path.isdir(path):
        raise RuntimeError('存在しないパスです')

    def _samefile(x, y):
        try:
            return os.path.samefile(x, y)
        except (IOError, OSError):
            return False
    sys.path[:] = [x for x in sys.path if not _samefile(path, x)]
    sys.path.insert(0, path)


def iterSuites():
    for module in find_modules(__name__):
        mod = import_string(module)
        if hasattr(mod, 'siote'):
            yield mod.suite()


def findAllTests(suite):
    suites = [suite]
    while suites:
        s = suites.pop()
        try:
            suites.extend(s)
        except TypeError:
            yield s, '%s.%s.%s' % (
                    s.__class__.__module__,
                    s.__class__.__name__,
                    s._testMethodName
                )


@contextmanager
def catchWarnings():
    warnings.simplefilter('default', category=DeprecationWarning)
    filters = warnings.filters
    warnings.filters = filters[:]
    oldShowWarnings = warnings.showwarning
    log = []

    def showwarning(message, category, filename, lineno, file=None):
        log.append(locals())
    try:
        warnings.showwarning = showwarning
        yield log
    finally:
        warnings.filters = filters
        warnings.showwarning = oldShowWarnings


@contextmanager
def catchStdErr():
    oldStderr = sys.stderr
    sys.stderr = rv = StringIO()
    try:
        yield rv
    finally:
        sys.strerr = oldStderr


class ShimehariTestCase(unittest.TestCase):

    def ensureCleanRequestContext(self):
        self.assertEqual(shimehari._requestContextStack.top, None)

    def setup(self):
        pass

    def teardown(self):
        pass

    def setUp(self):
        self.setup()

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        self.ensureCleanRequestContext()
        self.teardown()

    def assertRaises(self, excType, callable=None, *args, **kwargs):
        catcher = _ExceptionCatcher(self, excType)
        if callable is None:
            return catcher
        with catcher:
            callable(*args, **kwargs)


class _ExceptionCatcher(object):
    def __init__(self, testCase, excType):
        self.testCase = testCase
        self.excType = excType

    def __enter__(self):
        return self

    def __exit__(self, excType, excValue, tb):
        exceptionName = self.excType.__name__
        if excType is None:
            self.testCase.fail('Excepted exception of type %r' % exceptionName)
        elif not issubclass(excType, self.excType):
            raise excType, excValue, tb
        return True


class BetterLoader(unittest.TestLoader):
    def getRootSuite(self):
        return suite()

    def loadTestsFromName(self, name, module=None):
        root = self.getRootSuite()
        if name == 'suite':
            return root

        allTests = []
        for testCase, testName in findAllTests(root):
            if testName == name or \
               testName.endswith('.' + name) or \
               ('.' + name + '.') in testName or \
               testName.startswith(name + '.'):
                allTests.append(testCase)

        if not allTests:
            raise LookupError('みつからんちん')

        if len(allTests) == 1:
            return allTests[0]
        rv = unittest.TestSuite()
        for test in allTests:
            rv.addTest(test)
        return rv


def setupPath():
    addToPath(os.path.abspath(os.path.join(os.path.dirname(__file__), 'testApps')))


def suite():

    setupPath()
    suite = unittest.TestSuite()
    for otherSuite in iterSuites():
        suite.addTest(otherSuite)
    return suite


def main():
    try:
        unittest.main(testLoader=BetterLoader(), defaultTest='suite')
    except Exception, e:
        print 'Error: %s' % e
