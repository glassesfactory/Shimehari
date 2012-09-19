#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
===============================
    Shimehari.core.cache
    ~~~~~~~~~~~~~~~~~~~~~~~

    キャッシュストア
    
===============================
"""


import os
try:
    from hashlib import md5
except ImportError, e:
    from md5 import new as md5
import tempfile

from itertools import izip
from time import time




try:
    import cPickle as msg
except ImportError, e:
    import pickle as msg


def _items(mappp):
    return mappp.iteritems() if hasattr(mappp, 'iteritems') else mappp


u"""-----------------------------
    Shimehari.core.cachestore.BaseCacheStore
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    キャッシュストアの抽象クラス

------------------------------"""
class BaseCacheStore(object):

    def __init__(self, default_timeout=300):
        self.default_timeout = default_timeout


    u"""-----------------------------
        Shimehari.core.cachestore.BaseCacheStore
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        get

        キャッシュストアから指定されたキーの値を取得します。
        [args]
            :key　   取得したいキャッシュのキー

    ------------------------------"""
    def get(self, key):
        pass



    u"""-----------------------------
        Shimehari.core.cachestore.BaseCacheStore
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        getMany

        複数のキーからまとめてキャッシュを取得します。
        [args]
            :kyes   取得したいキャッシュのキー

    ------------------------------"""
    def getMany(self, *keys):
        return map(self.get, keys)



    u"""-----------------------------
        Shimehari.core.cachestore.BaseCacheStore
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        clear

        複数のキーからまとめてキャッシュを dict として取得します。
        [args]
            :key

    ------------------------------"""
    def getDict(self, *keys):
        return dict(izip(keys, self.getMany(*keys)))



    u"""-----------------------------
        Shimehari.core.cachestore.BaseCacheStore
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        delete

        指定されたキーをもつキャッシュを削除します。
        [args]
            :key

    ------------------------------"""
    def delete(self, key):
        pass



    u"""-----------------------------
        Shimehari.core.cachestore.BaseCacheStore
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        set

        キャッシュを追加します。
        [args]
            :key        キー
            :value      キャッシュしたい値
            :timeout    有効期限

    ------------------------------"""
    def set(self, key, value, timeout=None):
        pass



    u"""-----------------------------
        Shimehari.core.cachestore.BaseCacheStore
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        add

        キャッシュを追加します。
        [args]
            :key        キー
            :value      値
            :timeout    有効期限

    ------------------------------"""
    def add(self, key, value, timeout=None):
        pass



    u"""-----------------------------
        Shimehari.core.cachestore.BaseCacheStore
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        setMany

        複数のオブジェクトをまとめてキャッシュします。
        [args]
            :mapping    キャッシュしたいオブジェクトたちのキーマッピング
            :timeout    有効期限

    ------------------------------"""
    def setMany(self, mapping, timeout=None):
        for k, v in _items(mapping):
            self.set(k, v,timeout)



    u"""-----------------------------
        Shimehari.core.cachestore.BaseCacheStore
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        deleteMany

        複数のキーからまとめてキャッシュを消去します。
        [args]
            :keys キー達

    ------------------------------"""
    def deleteMany(self, *keys):
        [ self.delete(k) for k in keys ]



    u"""-----------------------------
        Shimehari.core.cachestore.BaseCacheStore
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        clear

        ストアの中のキャッシュを全て消去します
        [args]
            :key

    ------------------------------"""
    def clear(self):
        pass


class NullCacheStore(BaseCacheStore):
    pass

u"""-----------------------------
    Shimehari.core.cachestore.SimpleCacheStore
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    メモリ上に突っ込むシンプルなキャッシュ

    ------------------------------"""
class SimpleCacheStore(BaseCacheStore):
    def __init__(self, threshold=500, default_timeout=300):
        BaseCacheStore.__init__(self, default_timeout)
        self._cache = {}
        self.clear = self._cache.clear
        self._threshold = threshold



    u"""-----------------------------
        Shimehari.core.cachestore._prune
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        _prune

        有効期限の切れたキャッシュを消します。

    ------------------------------"""
    def _prune(self):
        #キャッシュの数が増えた時消す
        if len(self._cache) > self._threshold:
            now = time()
            for ind, (expires, _) in enumerate(self._cache.items()):
                if expires <= now or ind % 3 == 0:
                    self._cache.pop(key, None)



    u"""-----------------------------
        Shimehari.core.cachestore.SimpleCacheStore
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        get

        キャッシュを取得します。

    ------------------------------"""
    def get(self, key):
        now = time()
        expires, value = self._cache.get(key, (0, None))
        if expires > time():
            return msg.loads(value)



    u"""-----------------------------
        Shimehari.core.cachestore.SimpleCacheStore
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        set

        キャッシュを追加します。

    ------------------------------"""
    def set(self, key, value, timeout=None):
        if timeout is None:
            timeout = self.default_timeout

        self._prune()
        self._cache[key] = (time() + timeout, msg.dumps(value, msg.HIGHEST_PROTOCOL))


    u"""-----------------------------
        Shimehari.core.cachestore.SimpleCacheStore
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        add

        キーをチェックして存在していなかった時キャッシュを追加します。

    ------------------------------"""
    def add(self, key, value, timeout=None):
        if timeout is None:
            timeout = self.default_timeout

        if len(self._cache) > self._threshold:
            self._prune()
        item = (time() + timeout, msg.dumps(value, msg.HIGHEST_PROTOCOL))
        self._cache.setdefault(key, item)



    u"""-----------------------------
        Shimehari.core.cachestore.SimpleCacheStore
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        delete

        指定されたキーのキャッシュを削除します。

    ------------------------------"""
    def delete(self, key):
        self._cache.pop(key, None)


import re
from shimehari.core.helpers import importPreferredMemcachedClient
u"""-----------------------------
    Shimehari.core.cachestore.MemcachedCacheStore
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Memcache を使ったキャッシュストア
    ------------------------------"""
_testMemcachedKey = re.compile(r'[^\x00-\x21\xff]{1,250}$').match
class MemcachedCacheStore(BaseCacheStore):
    def __init__(self, servers=None, default_timeout=300, key_prefix=None):
        BaseCacheStore.__init__(self, default_timeout)
        if servers is None or isinstance(servers, (list,tuple)):
            if servers is None:
                servers = ['127.0.0.1:11211']
            self._client = importPreferredMemcachedClient(servers)
            if servers is None:
                raise RuntimeError('emcache nai jan')
        else:
            self._client = servers

        self.key_prefix = key_prefix



    u"""-----------------------------
        Shimehari.core.cachestore.MemcachedCacheStore
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        get

        指定したキーからキャッシュを取得します。
        [args]
            :key キー
        [return]
            キャッシュ

    ------------------------------"""
    def get(self, key):
        if isinstance(key,unicode):
            key = key.encode('utf-8')
        if self.key_prefix:
            key = self.key_prefix + key

        if _testMemcachedKey(key):
            return self._client.get(key)



    u"""-----------------------------
        Shimehari.core.cachestore.MemcachedCacheStore
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        getDict

        複数のキーからまとめてキャッシュを取得し、dict で返します。
        [args]
            :keys   キー
        [return]
            :dict   キャッシュ

    ------------------------------"""
    def getDict(self, *keys):
        keyMap = {}
        haveEncodedKeys = False
        for key in keys:
            if isinstance(key, unicode):
                encodedKey = key.encode('utf-8')
                haveEncodedKeys = True
            else:
                encodedKey = key
            if self.key_prefix:
                encodedKey = self.key_prefix + encodedKey
            if _testMemcachedKey(encodedKey):
                keyMap[encodedKey] = key
        d = rv = self._client.get_multi(keyMap.keys())
        if haveEncodedKeys or self.key_prefix:
            rv = {}
            for k, v in d.iteritems():
                rv[keyMap[k]] = v
        if len(rv) < len(keys):
            for k in keys:
                if k not in rv:
                    rv[k] = None
        return rv



    u"""-----------------------------
        Shimehari.core.cachestore.MemcachedCacheStore
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        getMany

        複数のキーからまとめてキャッシュを取得します。

    ------------------------------"""
    def getMany(self, *keys):
        d = self.getDict(*keys)
        return [d[k] for k in keys ]



    u"""-----------------------------
        Shimehari.core.cachestore.MemcachedCacheStore
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        set

        キャッシュを追加します。
        [args]
            :key        キャッシュのキー
            :value      キャッシュしたい値
            :timeout    有効期限

    ------------------------------"""
    def set(self, key, value, timeout=None):
        if timeout is None:
            timeout = self.default_timeout
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if self.key_prefix:
            key = self.key_prefix + key
        self._client.set(key, value, timeout)
        


    u"""-----------------------------
        Shimehari.core.cachestore.MemcachedCacheStore
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        setMany

        まとめて追加

    ------------------------------"""
    def setMany(self, mapping, timeout=None):
        if timeout is None:
            timeout = self.default_timeout
        newMap = {}
        for k, v in _items(mapping):
            if isinstance(k, unicode):
                k = k.encode('utf-8')
            if self.key_prefix:
                k = self.key_prefix + k
            newMap[k] = v
        self._client.set_multi(newMap, timeout)



    u"""-----------------------------
        Shimehari.core.cachestore.MemcachedCacheStore
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        add

        キャッシュを上書き

    ------------------------------"""
    def add(self, key, value, timeout=None):
        if timeout is None:
            timeout = self.default_timeout
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if self.key_prefix:
            key = self.key_prefix + key
        self._client.add(key, value, timeout)



    u"""-----------------------------
        Shimehari.core.cachestore.MemcachedCacheStore
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        delete

        キーで指定したキャッシュを削除
        [args]
            :key    削除したいキャッシュのキー

    ------------------------------"""
    def delete(self, key):
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if self.key_prefix:
            key = self.key_prefix + key
        if _testMemcachedKey(key):
            self._client.delete(key)



    u"""-----------------------------
        Shimehari.core.cachestore.MemcachedCacheStore
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        deleteMany

        まとめて削除

    ------------------------------"""
    def deleteMany(self, *keys):
        newKeys = []
        for k in keys:
            if isinstance(k, unicode):
                k = k.encode('utf-8')
            if self.key_prefix:
                k = self.key_prefix + k
            if _testMemcachedKey(k):
                newKeys.append(k)
        self._client.delete_multi(newKeys)

    def clear(self):
        self._client.flush_all()



u"""-----------------------------
    Shimehari.core.cachestore.FileSystemCacheStore
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    FileSystem を使ったキャッシュストア

------------------------------"""
_fsTransactionSuffix ='.__sakekasu'
class FileSystemCacheStore(BaseCacheStore):
    def __init__(self, cacheDir, threshold=500, default_timeout=300, mode=0600):
        BaseCacheStore.__init__(self, default_timeout)
        self._cacheDir = cacheDir
        self._threshold = threshold
        self._mode = mode

        if not os.path.exists(self._cacheDir):
            os.makedirs(self._cacheDir)


    u"""-----------------------------
        Shimehari.core.cachestore.FileSystemCacheStore
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        _getFileList

        キャッシュディレクトリ内のキャッシュ一覧を返します。

    ------------------------------"""
    def _getFileList(self):
        return [os.path.join(self._cacheDir, fn) for fn in os.listdir(self._cacheDir) if not fn.endswith(_fsTransactionSuffix)]



    u"""-----------------------------
        Shimehari.core.cachestore.FileSystemCacheStore
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        _getFileName

        ファイル名を返します。

    ------------------------------"""
    def _getFileName(self, key):
        hash = md5(key).hexdigest()
        return os.path.join(self._cacheDir, hash)



    u"""-----------------------------
        Shimehari.core.cachestore.FileSystemCacheStore
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        _prune

        有効期限の切れたキャッシュを消します。

    ------------------------------"""
    def _prune(self):
        entries = self._getFileList()
        if len(entries) > self._threshold:
            now = time()
            for ind, fn in enumerate(entries):
                remove = None
                f = None
                try:
                    try:
                        f = open(fn, 'rb')
                        expires = msg.load(f)
                        remove = expires <= now or ind % 3 == 0
                    except (IOError, OSError):
                        pass
                    finally:
                        if f is not None:
                            f.close()
                except Exception:
                    pass

                if remove:
                    try:
                        os.remove(fn)
                    except (IOError, OSError):
                        pass



    u"""-----------------------------
        Shimehari.core.cachestore.FileSystemCacheStore
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        get

        指定されたキーからキャッシュを取得します。
        [args]
            :key    取得したいキャッシュのキー
        [return]
            :value  キャッシュ

    ------------------------------"""
    def get(self, key):
        fn = self._getFileName(key)
        try:
            f = open(fn, 'rb')
            try:
                if msg.load(f) >= time():
                    return msg.load(f)
            finally:
                f.close()
            os.remove(fn)
        except Exception:
            return None



    u"""-----------------------------
        Shimehari.core.cachestore.FileSystemCacheStore
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        set

        新たなキャッシュを追加します。
        [args]
            :key        キー
            :value      追加したい値
            :timeout    有効期限

    ------------------------------"""
    def set(self, key, value, timeout=None):
        if timeout is None:
            timeout = self.default_timeout
        fn = self._getFileName(key)
        self._prune()
        try:
            fd, tmp = tempfile.mkstemp(suffix=_fsTransactionSuffix, dir=self._cacheDir)
            f = os.fdopen(fd, 'wb')
            try:
                msg.dump(int(time() + timeout), f, 1)
                msg.dump(value, f, msg.HIGHEST_PROTOCOL)
            finally:
                f.close()
            os.rename(tmp, fn)
            os.chmod(fn, self._mode)
        except (IOError, OSError), e:
            pass



    u"""-----------------------------
        Shimehari.core.cachestore.FileSystemCacheStore
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        add

        キャッシュを追加します。
        [args]
            :key        追加したいキー
            :value      追加したい値
            :timeout    有効期限

    ------------------------------"""
    def add(self, key, value, timeout=None):
        fn = self._getFileName(key)
        if not os.path.exists(fn):
            self.set(key, value, timeout)



    u"""-----------------------------
        Shimehari.core.cachestore.FileSystemCacheStore
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        delete

        指定されたキャッシュを削除します
        [args]
            :key 削除したいキャッシュのキー

    ------------------------------"""
    def delete(self, key):
        try:
            os.remove(self._getFileName(key))
        except (IOError, OSError):
            pass



    u"""-----------------------------
        Shimehari.core.cachestore.FileSystemCacheStore
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        clear

        キャッシュを全て削除します。

    ------------------------------"""
    def clear(self):
        for fn in self._getFileList():
            try:
                os.remove(fn)
            except (ImportError, OSError):
                pass



u"""-----------------------------
    Shimehari.core.cachestore.RedisCacheStore
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Redis を使ったキャッシュストア

------------------------------"""
class RedisCacheStore(BaseCacheStore):
    def __init__(self, host='localhost', port=6379, passwd=None, default_timeout=300, key_prefix=None):
        BaseCacheStore.__init__(self, default_timeout)
        if isinstance(host, basestring):
            try:
                import redis
            except ImportError, e:
                raise RuntimeError('no redis module')
            self._client = redis.Redis(host=host, port=port, password=passwd)
        else:
            self._client = host
        self.key_prefix = key_prefix or ''



    u"""-----------------------------
        Shimehari.core.cachestore.RedisCacheStore
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        dump

        与えられた値をシリアライズします。  
        [args]
            :value  シリアライズしたい値

    ------------------------------"""
    def dump(self, value):
        t = type(value)
        if t is int or t is long:
            return str(value)
        else:
            return '!' + msg.dumps(value)



    u"""-----------------------------
        Shimehari.core.cachestore.RedisCacheStore
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        load

        シリアライズされたものを復元します。
        [args]
            :value  復元したい項目

    ------------------------------"""
    def load(self, value):
        if value is None:
            return None
        if value.startswith('!'):
            return msg.loads(value[1:])
        try:
            return int(value)
        except ValueError:
            return value


    u"""-----------------------------
        Shimehari.core.cachestore.RedisCacheStore
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        get

        指定されたキーのキャッシュを取得します
        [args]
            :key    キー

        [return]
            キャッシュ

    ------------------------------"""
    def get(self, key):
        return self.load(self._client.get(self.key_prefix + key))



    u"""-----------------------------
        Shimehari.core.cachestore.RedisCacheStore
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        getMany

        複数のキーからまとめて取得します。
        [args]
            :keys   キー達
        [return]
            キャッシュ

    ------------------------------"""
    def getMany(self, *keys):
        if self.key_prefix:
            keys = [self.key_prefix + k for k in keys]
        return [self.load(x) for x in self._client.mget(keys)]



    u"""-----------------------------
        Shimehari.core.cachestore.RedisCacheStore
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        set

        キャッシュを追加します。
        [args]
            :key        キー
            :value      キャッシュしたい項目
            :timeout    有効期限

    ------------------------------"""
    def set(self, key, value, timeout=None):
        if timeout is None:
            timeout = self.default_timeout
        dump = self.dump(value)
        self._client.setex(self.key_prefix + key, dump, timeout)



    u"""-----------------------------
        Shimehari.core.cachestore.RedisCacheStore
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        setMany

        まとめて複数のキャッシュを追加します
        [args]
            :mapping    まとめて追加したい項目
            :timeout    有効期限

    ------------------------------"""
    def setMany(self, mapping, timeout=None):
        if timeout is None:
            timeout = self.default_timeout
        pipe = self._client.pipeline()
        for k, v in _items(mapping):
            dump = self.dump(v)
            pipe.setex(self.key_prefix + k, v, timeout)
        pipe.execute()



    u"""-----------------------------
        Shimehari.core.cachestore.RedisCacheStore
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        add

        指定されたキーのキャッシュを削除します。
        [args]
            :key

    ------------------------------"""
    def add(self, key, value, timeout=None):
        if timeout is None:
            timeout = self.default_timeout
        dump = self.dump(value)
        added = self._client.setnx(self.key_prefix + key, value)
        if added:
            self._client.expire(self.key_prefix + key, timeout)



    u"""-----------------------------
        Shimehari.core.cachestore.RedisCacheStore
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        delete

        指定されたキーのキャッシュを削除します。
        [args]
            :key    キー

    ------------------------------"""
    def delete(self, key):
        self._client.delete(self.key_prefix + key)



    u"""-----------------------------
        Shimehari.core.cachestore.RedisCacheStore
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        deleteMany

        複数のキーからまとめてキャッシュを削除します。
        [args]
            :keys   キー

    ------------------------------"""
    def deleteMany(self, *keys):
        if not keys:
            return
        if self.key_prefix:
            keys = [self.key_prefix + k for k in keys]
        self._client.delete(*keys)



    u"""-----------------------------
        Shimehari.core.cachestore.RedisCacheStore
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        clear

        キャッシュストアの中身を全て消去します。

    ------------------------------"""
    def clear(self):
        if self.key_prefix:
            keys = self._client.keys(self.key_prefix + '*')
            if keys:
                self._client.delete(*keys)
        self._client.flushdb()

