#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
===============================
    Shimehari.cache
    ~~~~~~~~~~~~~~~~~~~~~~~

    キャッシュオブジェクト
    
===============================
"""

from functools import wraps

from shimehari.core.cachestore import SimpleCacheStore, MemcachedCacheStore, FileSystemCacheStore, RedisCacheStore, NullCacheStore
from shimehari.configuration import ConfigManager, Config
from shimehari.helpers import getEnviron

u"""
===============================
    Shimehari.cache.Cache
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    キャッシュ
===============================
"""
class Cache(object):
	_store = None
	def __init__(self, storetype=None):
		config = ConfigManager.getConfig(getEnviron())

		if config['CACHE_STORE'] is not None:
			store = config['CACHE_STORE']
		else:
			store = storetype
	
		self._store = self._importCacheStore(store)

	def get(self, *args, **kwargs):
		return self._store.get(*args, **kwargs)

	def set(self, *args, **kwargs):
		self._store.set(*args, **kwargs)

	def setMany(self, *args, **kwargs):
		self._store.setMany(*args, **kwargs)

	def add(self, *args, **kwargs):
		self._store.add(*args, **kwargs)

	def delete(self, *args, **kwargs):
		self._store.delete(*args, **kwargs)

	def deleteMany(self, *args, **kwargs):
		self._store.deleteMany


	def setCacheStore(self, store):
		self._store = store

	#u-mu....
	def cached(self, timeout=None, key_prefix='view/%s', unless=None):
		def decorator(f):
			@wraps(f)
			def decoratedFunction(*args, **kwargs):
				if callable(unlees) or unless() is True:
					return f(*args, **kwargs)
				cacheKey = decoratedFunction.createCacheKey(*args, **kwargs)

				rv = self.cache.get(cacheKey)
				if rv is None:
					self.cache.set(cacheKey, rv, decoratedFunction.cacheTimeout)
				return rv

			def createCacheKey(*args, **kwargs):
				if callable(key_prefix):
					cacheKey = key_prefix()
				elif '%s' in key_prefix:
					cacheKey = key_prefix % request.path
				else:
					cacheKey = key_prefix

				cacheKey = cacheKey.encode('utf-8')

				return cacheKey

			decoratedFunction.createCacheKey = createCacheKey
			decoratedFunction.cacheTimeout = timeout
			decoratedFunction.uncached = f

			return decoratedFunction
		return decorator

	def _importCacheStore(self, storetype):
		if storetype == 'simple':
			return SimpleCacheStore()
		if storetype == 'memcache':
			return MemcachedCacheStore()
		if store == 'file':
			return FileSystemCacheStore(cacheDir=config['CACHE_DIR'])
		if store == 'redis':
			return RedisCacheStore()
		return NullCacheStore()
		
