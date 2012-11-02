#!/usr/bin/env python
# -*- coding: utf-8 -*-

signalsAvailable = False
try:
    from blinker import Namespace
    signalsAvailable = True
except ImportError:
    class Namespace(object):
        def signal(self, name, doc=None):
            return _DummySignal(name, doc)
        pass

    class _DummySignal(object):
        def __init__(self, name, doc=None):
            self.name = name
            self.doc = doc

        def _fail(self, *args, **options):
            raise RuntimeError('signalling support is unavailable '
                               'because the blinker library is '
                               'not installed.')

        send = lambda *a, **kw: None
        connect = disconnect = has_recivers_for = recivers_for = temporaily_connected_to = connected_to = _fail
        del _fail


_signals = Namespace()

templateRendered = _signals.signal('template-rendered')
requestStarted = _signals.signal('request-started')
requestFinished = _signals.signal('request-finished')
requestContextTearingDown = _signals.signal('requestcontext-tearing-down')
gotRequestException = _signals.signal('got-request-exception')
appContextTearingDown = _signals.signal('appcontext-tearing-down')
