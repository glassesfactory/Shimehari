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
from shimehari.shared import request, currentApp

u"""
===============================
    Shimehari.cache.Cache
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    キャッシュ
===============================
"""
class Cache(object):
    store = None
    def __init__(self, storetype=None):
        config = ConfigManager.getConfig(getEnviron())

        if config['CACHE_STORE'] is not None:
            store = config['CACHE_STORE']
        else:
            store = storetype
    
        self.store = self._importCacheStore(store)


    u"""-----------------------------
        Shimehari.cache.Cache
        ~~~~~~~~~~~~~~~~~~~~~~~~
        get

        キャッシュストアから指定したキーに該当するキャッシュを取得します。
        [args]
            :keys   キー

        [return]
            :value  キャッシュ

    ------------------------------"""
    def get(self, *args, **kwargs):
        return self.store.get(*args, **kwargs)

    def getMany(self, *args, **kwargs):
        return self.store.getMany(*args, **kwargs)

    def getDict(self, *args, **kwargs):
        return self.store.getDict(*args, **kwargs)

    def set(self, *args, **kwargs):
        self.store.set(*args, **kwargs)

    def setMany(self, *args, **kwargs):
        self.store.setMany(*args, **kwargs)

    def add(self, *args, **kwargs):
        self.store.add(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.store.delete(*args, **kwargs)

    def deleteMany(self, *args, **kwargs):
        self.store.deleteMany(*args, **kwargs)

    def clear(self):
        self.store.clear()


    def setCacheStore(self, store):
        self.store = store

    #u-mu....
    def cached(self, timeout=None, key_prefix='view/%s', unless=None):
        def decorator(f):
            @wraps(f)
            def decoratedFunction(*args, **kwargs):
                if callable(unless) and unless() is True:
                    return f(*args, **kwargs)
                cacheKey = decoratedFunction.createCacheKey(*args, **kwargs)

                rv = self.store.get(cacheKey)
                if rv is None:
                    rv = f(*args, **kwargs)
                    self.store.set(cacheKey, rv, decoratedFunction.cacheTimeout)
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
        if storetype == 'file':
            config = ConfigManager.getConfig(getEnviron())
            return FileSystemCacheStore(cacheDir=config['CACHE_DIR'])
        if storetype == 'redis':
            return RedisCacheStore()
        return NullCacheStore()
        
