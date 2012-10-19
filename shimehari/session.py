#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
===============================
    Shimehari.session
    ~~~~~~~~~~~~~~~~~
    セッション管理
===============================
"""
from datetime import datetime
from werkzeug.contrib.securecookie import SecureCookie
from werkzeug.contrib.sessions import SessionStore as SessionStoreBase, generate_key
from shimehari.configuration import ConfigManager
from shimehari.helpers import jsonAvailable
from shimehari.core.helpers import importPreferredMemcachedClient


"""シリアライズで使用するモジュールを決定します。"""
try:
    import msgpack as msg
except ImportError:
    try:
        import cpickle as msg
    except ImportError:
        import pickle as msg
    finally:
        if not jsonAvailable:
            raise RuntimeError('you do not have selializer')
        from shimehari.helpers import json as msg


u"""
===============================
    ::pkg:: Shimehari.sessions
    SessionMixin
    ~~~~~~~~~~~~

    セッションの機能をもたせます

===============================
"""


class SessionMixin(object):
    def _get_permanent(self):
        return self.get('_permanent', False)

    def _set_permanent(self, value):
        self['_permanent'] = bool(value)

    permanent = property(_get_permanent, _set_permanent)
    del _get_permanent, _set_permanent

    new = False
    modified = True


u"""
===============================
    ::pkg:: Shimehari.sessions
    SecureCookieSession
    ~~~~~~~~~~~~~~~~~~~

    SecureCookie を使ったセッション

===============================
"""


class SecureCookieSession(SecureCookie, SessionMixin):
    u"""SecureCookie を使ったセッションクラス

    :param initial:     セッションデータ
    :param sid:         セッションID
    :param new:         新規セッション
    """
    def __init__(self, initial=None, sid=None, new=False, secret_key=None):
        def on_update(self):
            self.modified = True
        SecureCookie.__init__(self, initial, secret_key=secret_key, new=new)
        self.sid = sid
        self.new = new
        self.modified = False

        if self.sid is None:
            self.sid = generate_key()

    @classmethod
    def load_cookie(cls, request, sid=None, key='session', secret_key=None):
        data = request.cookies.get(key)
        if not data:
            return cls(sid=sid, secret_key=secret_key)
        return cls.unserialize(data, secret_key=secret_key, sid=sid)

    @classmethod
    def unserialize(cls, string, secret_key, sid=None):
        u"""werkzeug.contrib.securecookie.SecureCookie.unserialize"""
        items = SecureCookie.unserialize(string, secret_key).items()
        return cls(items, sid=sid, secret_key=secret_key, new=False)


u"""
===============================
    ::pkg:: Shimehari.sessions
    NullSession
    ~~~~~~~~~~~

    物言わぬセッション

===============================
"""


class NullSession(SecureCookieSession):
    def _fail(self, *args, **kwargs):
        raise RuntimeError('Null Session!!!')

    __setitem__ = __delitem__ = clear = pop = popitem = setdefault = update = _fail
    del _fail


u"""
===============================
    ::pkg:: Shimehari.sessions
    _SessionStore
    ~~~~~~~~~~~~~

    werkzeug のセッションストアに多少機能を追加します。

===============================
"""


class _SessionStore(SessionStoreBase):
    nullSessionClass = NullSession

    def save(self, session, response):
        return NotImplementedError()

    def isNullSession(self, session):
        return isinstance(session, self.nullSessionClass)

    def makeNullSession(self):
        return self.nullSessionClass()


class MemcachedSessionStore(_SessionStore):
    u"""セッションの保存先に Memcache を使ったセッションストア

    :param servers:         Memcache サーバー
    :param keyPrefix:       セッション格納時、キーに付ける接頭詞
    :param defaultTimeout:  セッションの保存期間
    :param session_class:   セッションクラス
    """
    def __init__(self, servers=None, keyPrefix=None, defaultTimeout=300, session_class=None):
        _SessionStore.__init__(self, session_class=session_class)

        if isinstance(servers, (list, tuple)):
            client = importPreferredMemcachedClient(servers)
        elif servers is not None:
            client = servers
        else:
            raise RuntimeError('no memcache module.')

        self._memcacheClient = client
        self._memcacheKeyPrefix = keyPrefix
        self._memcacheTimeout = defaultTimeout

    def save(self, session, response):
        key = self._getMemcacheKey(session.sid)
        data = msg.dumps(dict(session))
        self._memcacheClient.set(key, data)

    def delete(self, session):
        self._memcacheClient.delete(self._getMemcacheKey(session.sid))

    def get(self, sid):
        if not self.is_vaild_key(sid):
            return self.new()

        key = self._getMemcacheKey(sid)
        packed = self._memcacheClient.get(key)
        try:
            data = msg.loads(packed)
        except TypeError:
            data = {}
        return self.session_class(data, sid, False)

    def _getMemcacheKey(self, sid):
        if self._memcacheKeyPrefix:
            key = self._memcacheKeyPrefix + sid
        else:
            key = sid
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        return key

from shimehari.shared import request


class SecureCookieSessionStore(_SessionStore):
    u"""SecureCookieSession を利用したセッションストア"""
    def __init__(self, key='session', expire=0):
        _SessionStore.__init__(self, session_class=SecureCookieSession)
        self.key = key
        #直せ
        self.path = '/'
        #直せ
        self.domain = None

    def getCookieHttpOnly(self):
        return ConfigManager.getConfig()['SESSION_COOKIE_HTTPONLY']

    def getCookieSecure(self):
        return ConfigManager.getConfig()['SESSION_COOKIE_SECURE']

    def getCookieExpire(self, session):
        if session.permanent:
            return datetime.utcnow() + ConfigManager.getConfig()['PERMANENT_SESSION_LIFETIME']

    def new(self):
        config = ConfigManager.getConfig()
        key = config['SECRET_KEY']
        sessionCookieName = config['SESSION_COOKIE_NAME']
        if key is not None:
            return self.session_class.load_cookie(request, key=sessionCookieName, secret_key=key)

    def save(self, session, response):
        self.expire = self.getCookieExpire(session)
        self.httponly = self.getCookieHttpOnly()
        self.secure = self.getCookieSecure()
        if session.modified and not session:
            response.delete_cookie(self.key, path=self.path, domain=self.domain)
        else:
            session.save_cookie(response, self.key, path=self.path, expires=self.expire, httponly=self.httponly,
                secure=self.secure, domain=self.domain)

    def delete(self, session):
        session.pop(self.key, None)

    #hum...
    def get(self, sid):
        if not self.is_valid_key(sid):
            return self.new()
        config = ConfigManager.getConfig()
        key = config['SECRET_KEY']
        sessionCookieName = config['SESSION_COOKIE_NAME']
        if key is not None:
            return self.session_class.load_cookie(request, key=sessionCookieName, secret_key=key, sid=sid)


class RedisSessionStore(_SessionStore):
    u"""Redis を使ったセッションストア

    Author: @soundkitchen Izukawa Takanobu

    :param
    """
    def __init__(self, host='localhost', port=6379, db=0, expire=0, session_class=None):
        from redis import Redis
        super(RedisSessionStore, self).__init__(session_class=session_class)
        self._conn = Redis(host=host, port=port, db=db)
        self._expire = int(expire)

    def save(self, session):
        packed = msg.dumps(dict(session))
        self._conn.set(session.sid, packed)

    def delete(self, session):
        self._conn.delete(session.sid)

    def get(self, sid):
        if not self.is_valid_key(sid):
            return self.new()

        packed = self._conn.get(sid)
        try:
            data = msg.loads(packed, encoding='utf-8')
            if self._expire:
                self._conn.expire(sid, self._expire)
        except TypeError:
            data = {}
        return self.session_class(data, sid, False)


u"""デフォルトのセッションストアを決定します。"""
_currentStore = None
try:
    from werkzeug.contrib.sessions import FileSystemSessionStore
    _currentStore = FileSystemSessionStore()
except (Exception, RuntimeError), e:
    try:
        u"""GAE 対策"""
        _currentStore = MemcachedSessionStore()
    except (Exception, RuntimeError), e:
        u"""それでもダメだったら最後の手段"""
        _currentStore = SecureCookieSessionStore()
finally:
    SessionStore = _currentStore.__class__
