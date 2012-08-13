#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
===============================
    Shimehari.core
    helpers
    ~~~~~~~
    
    主に Shimehari 内部で使われることを
    想定した helper 

===============================
"""

import sys

u"""--------------------------------------
    ::pkg:: Shimenari.core.helpers
    importFromString
    ~~~~~~~~~~~~~~~~

    アプリを走らせます。
    drink のラッパー。
    WSGI 周りのライブラリとかで
    run を自動的に呼ぶ物対策
--------------------------------------"""
def importFromString(targetName):
    if isinstance(targetName, unicode):
        targetName = str(targetName)
    try:
        if '.' in targetName:
            pkgs, obj = targetName.rsplit('.',1)
        else:
            return __import__(targetName)
        try:
            return getattr(__import__(pkgs, fromlist=[obj]), obj)
        except (ImportError, AttributeError):
            pkgName = pkgs + '.' + obj
            __import__(pkgName)
            return sys.modname[pkgName]
            
    except ImportError, error:
        raise ImportError(error)


class DebugFilesKeyError(KeyError, AssertionError):
    def __init__(self, request, key):
        formMatches = request.form.getlist(key)
        buf = ['aaaa %s %s' %(key, request.mimetype)]

        if formMatches:
            buf.append('\n\n %s' % ''.join('"%s"' % x for x in formMatches))
        self.msg = ''.join(buf).encode('utf-8')

    def __str__(self):
        return self.msg
        

def attachEnctypeErrorMultidict(request):
    oldCls = request.files.__class__
    class newCls(oldCls):
        def __getitem__(self,key):
            try:
                return oldCls.__getitem__(self, key)
            except KeyError, error:
                if key not in request.form:
                    raise
                raise DebugFilesKeyError(request, key)
    newCls.__name__ = oldCls.__name__
    newCls.__module__ = oldCls.__module__
    request.files.__class__ = newCls



