#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
===============================
    ::pkg:: Shimehari.core.command
    AbstractCommand
    ~~~~~~~~~~~~~~~
    コマンドラインツール

    抽象クラス
    Command の元となるクラス
===============================
"""

import sys
from optparse import OptionParser, make_option
import traceback
import shimehari

from shimehari.core.exceptions import CommandError

class AbstractCommand(object):
    option_list = (
            make_option('--traceback', action='store_true', help='Print traceback on exception'),
        )
    help = ''
    args = ''

    def getVersion(self):
        return shimehari.getVersion()

    def usage(self, subcommand):
        usage = '%%prog %s [options] %s' % (subcommand, self.args)
        if self.help:
            return '%s\n\n%s' %(usage, self.help)
        else:
            return usage

    def createParser(self, progName, subcommand):
        return OptionParser(prog=progName, 
                            usage=self.usage(subcommand),
                            version=self.getVersion(),
                            option_list=self.option_list)

    def runFromArgv(self, argv):
        parser = self.createParser(argv[0], argv[1])
        options, args = parser.parse_args(argv[2:])
        self.execute(*args, **options.__dict__)

    def execute(self, *args, **options):
        
        showTraceback = options.get('traceback', False)

        try:
            self.stdout = options.get('stdout', sys.stdout)
            self.stderror = options.get('stderr', sys.stderr)

            output = self.handle(*args,**options)
            if output:
                self.stdout.write(output)
        except (TypeError,CommandError), e:
            if showTraceback:
                traceback.print_exc()
            else:
                self.stderror.write('%s\n' % unicode(e).encode('utf-8'))
            sys.exit(1)

    def validate(self):
        raise NotImplementedError()

    def handle(self):
        raise NotImplementedError()

    #humu...
    def getAppConfig(self):
        pass

import os

class CreatableCommand(AbstractCommand):

    u"""-----------------------------
        ::pkg:: Shimehari.core.manage.AbstractCommand.CreatableCommand
        toWritable
        ~~~~~~~~~~

        ファイルを書き込み可能状態にします。
        [args]
            :filename 対象ファイル名
    ------------------------------"""
    def toWritable(self,filename):
        if sys.platform.startswith('java'):
            return

        if not os.access(filename, os.W_OK):
            st = os.stat(filename)
            newPermission = stat.S_IMODE(st.st_mode)
            os.chmod(filename, newPermission)

