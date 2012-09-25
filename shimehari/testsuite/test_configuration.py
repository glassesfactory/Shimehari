#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from shimehari.testsuite import ShimehariTestCase
from shimehari.configuration import ConfigManager, Config


class TestConfigManager(ShimehariTestCase):
    def testHasNotConfig(self):
        ConfigManager.configrations = {}
        rv = ConfigManager.hasConfig()
        self.assertEqual(rv, False)

    def testAddConfig(self):
        config = Config()
        self.assertNotEqual(ConfigManager.addConfig(config), TypeError)

    def testAddConfigRaiseTypeError(self):
        dummy = u'|/ﾟUﾟ|丿'
        self.assertRaises(TypeError, ConfigManager.addConfig, dummy)

    def testAddConfigs(self):
        configA = Config()
        configB = Config('production')
        configC = Config('test')
        self.assertNotEqual(ConfigManager.addConfigs([configA, configB, configC]), TypeError)

    def testHasConfig(self):
        config = Config()
        ConfigManager.addConfig(config)
        rv = ConfigManager.hasConfig()
        self.assertEqual(rv, True)

    def testGetConfigs(self):
        configA = Config()
        configB = Config('production')
        ConfigManager.addConfigs([configA, configB])
        self.assertNotEqual(ConfigManager.getConfigs(), {})

    def testGetConfig(self):
        config = Config()
        ConfigManager.configrations = {}
        ConfigManager.addConfig(config)
        self.assertEqual(ConfigManager.getConfig('development'), config)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestConfigManager))
    return suite
