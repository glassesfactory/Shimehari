#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
===============================
    Shimehari.session
    ~~~~~~~~~~~~~~~~~
    セッション管理
===============================
"""

from werkzeug.contrib.securecookie import SecureCookie
from werkzeug.contrib.sessions import SessionStore as SessionStoreBase, Session
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
    u"""Secure Cookie つかった session"""
    def __init__(self,  initial=None, sid=None, new=False):
        def on_update(self):
            self.modified = True
        # SecureCookie.__init__(self, initial, on_update)
        self.sid = sid
        self.new = new
        self.modified = False





u"""
===============================
    ::pkg:: Shimehari.sessions
    NullSession
    ~~~~~~~~~~~

    物言わぬセッション
    
===============================
"""
class NullSession(Session):
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



u"""
===============================
    ::pkg:: Shimehari.sessions
    MemcachedSessionStore
    ~~~~~~~~~~~~~~~~~~~~~

    セッションの保存先として Memcache を
    使用します。
    
===============================
"""
from pickle import HIGHEST_PROTOCOL
class MemcachedSessionStore(_SessionStore):
    """session store using memcache"""
    def __init__(self,servers=None, keyPrefix=None, defaultTimeout=300, session_class=None):
        _SessionStore.__init__(self,session_class=session_class)

        if isinstance(servers, (list,tuple)):
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
        data = self._memcacheClient.get(key)
        try:
            data = msg.loads(packed)
        except TypeError:
            data = {}
        return self.session_class(data, sid, False)

    def _getMemcacheKey(self,sid):
        if self._memcacheKeyPrefix:
            key = self._memcacheKeyPrefix + sid
        else:
            key = sid
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        return key



u"""
===============================
    ::pkg:: Shimehari.sessions
    SecureCookieSessionStore
    ~~~~~~~~~~~~~~~~~~~~~~~~

    SecureCookieSession を利用したセッションストア
    
===============================
"""
from shimehari.shared import request
class SecureCookieSessionStore(_SessionStore):
    def __init__(self, key='session', expire=0):
        _SessionStore.__init__(self,session_class=SecureCookieSession)
        self.key = key
        #直せ
        self.path = '/'
        #直せ
        self.domain = None

    def save(self, session, response):
        if session.modified and not session:
            response.delete_cookie(self.key, path=self.path, domain=self.domain)
        else:
            session.save_session(response, self.key, path=self.path, expire=self.expire, httponly=self.httponly,
                secure=self.secure, domain=self.domain)

    def delete(self, session):
        session.pop(self.key, None)

    #hum...
    def get(self, sid):
        if not self.is_vaild_key(sid):
            return self.new()

        if self.key is not None:
            return self.session_class.load_cookie(request, self.key, secret_key=self.key)





u"""
===============================
    ::pkg:: Shimehari.session
    RedisSessionStore
    ~~~~~~~~~~~~~~~~~

    Author: @soundkitchen Izukawa Takanobu 
    Redis を使ったセッションストア
    
===============================
"""

class RedisSessionStore(_SessionStore):
    """session store using redis."""
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
        except TypeError, e:
            data = {}
        return self.session_class(data, sid, False)


"""デフォルトのセッションストアを決定します。"""
try:
    from werkzeug.contrib.sessions import FileSystemSessionStore
    _currentStore = FileSystemSessionStore()
except (Exception, RuntimeError), e:
    try:
        """GAE 対策"""
        _currentStore = MemcachedSessionStore()
    except (Exception, RuntimeError), e:
        """それでもダメだったら最後の手段"""
        _currentStore = SecureCookieSessionStore()
finally:
    SessionStore = _currentStore.__class__