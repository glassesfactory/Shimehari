#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
===============================
    Shimehari.core.manager
    ~~~~~~~~~~~~~~~~~~~~~~
    マネージメント
===============================
"""

import os
import sys
from optparse import OptionParser

from .AbstractCommand import AbstractCommand, CreatableCommand
from shimehari.core.helpers import importFromString

_commands = None


u"""
コマンドラインから色々実行するべさ
"""


def executeFromCommandLine(argv=None):
    executer = CommandLineExecuter(argv)
    executer.execute()


def loadCommandModule(cmdName, name):
    module = importFromString('.'.join([cmdName, name]))
    return module.Command()


def getCommands():
    global _commands
    if _commands is None:
        _commands = dict([(name, 'shimehari.core.manage.commands') for name in findCommand(__path__[0], 'commands')])
        #ユーザーコマンドー…
        _commands.update(dict([(name, 'command') for name in findCommand(os.getcwd(), 'command')]))
    return _commands


def findCommand(manageDir, commandDir):
    cmdDir = os.path.join(manageDir, commandDir)
    try:
        return [f[:-3] for f in os.listdir(cmdDir) if not f.startswith('_') and f.endswith('.py')]
    except OSError:
        return []


class CommandLineExecuter(object):
    def __init__(self, argv):
        self.argv = argv or sys.argv[:]
        self.progName = os.path.basename(self.argv[0])

    def fetchCommand(self, subcommand):
        try:
            cmdName = getCommands()[subcommand]
        except KeyError:
            sys.stdout.write("Unkown command: %r\nType %s help for usage. \n" % (subcommand, self.progName))
            sys.exit(1)
        if isinstance(cmdName, AbstractCommand):
            cls = cmdName
        else:
            cls = loadCommandModule(cmdName, subcommand)
        return cls

    def execute(self):
        parser = OptionParser()
        try:
            subcommand = self.argv[1]
        except:
            subcommand = 'help'

        if subcommand == 'version':
            from shimehari import getVersion
            sys.stdout.write('shimehari version: ' + getVersion() + '\n')
        elif self.argv[1:] == ['--version']:
            sys.stdout.write('shimehari version: ' + getVersion() + '\n')
        elif self.argv[1:] in (['--help'], ['-h']):
            self.fetchCommand('help').runFromArgv(self.argv)
        else:
            self.fetchCommand(subcommand).runFromArgv(self.argv)
