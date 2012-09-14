#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
===============================
    Shimehari.cache
    ~~~~~~~~~~~~~~~~~~~~~~~

    キャッシュオブジェクト
    
===============================
"""

from shimehari.configuration import ConfigManager, Config
from shimehari.helpers import getEnviron

class Cache(object):
	def __init__(self, app=None):
		config = ConfigManager.getConfig(getEnviron())

	def get(self, *args, **kwargs):
		pass

	def set(self, *args, **kwargs):
		pass

	def add(self, *args, **kwargs):
		pass

	def delete(self, *args, **kwargs):
		pass

	def deleteMany(self, *args, **kwargs):
		pass

	#u-mu....
	def cached(self):
		pass