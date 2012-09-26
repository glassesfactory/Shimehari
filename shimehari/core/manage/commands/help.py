#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
===============================
    Shimehari.core.manage.commands.help
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    help コマンド

    各コマンドモジュールは共通インターフェースとして
    Command クラスを持ちます。

===============================
"""

import sys
from pkgutil import walk_packages

from shimehari.core.manage import AbstractCommand
from shimehari.core.exceptions import CommandError
from shimehari.core.manage import commands
from shimehari.core.manage.AbstractCommand import command_dict


u"""
===============================
    ::pkg:: Shimehari.core.manage.commands.help
    Command
    ~~~~~~~
    コマンドの実装

===============================
"""


class Command(AbstractCommand):
    name = 'help'
    summary = "Show help on command (e.g. 'shimehari help drink')"
    usage = "Usage: %prog COMMAND [OPTIONS]"

    def __init__(self):
        super(Command, self).__init__()

    def handle(self, *args, **options):
        load_all_commands()

        if args:
            ## FIXME: handle errors better here
            command = args[0]
            if command not in command_dict:
                raise CommandError('No command with the name: %s' % command)
            command = command_dict[command]
            sys.stdout.write(command.summary + '\n\n')
            command.parser.print_help()
            return 0

        command = AbstractCommand()

        sys.stdout.write(command.summary + '\n\n')
        command.parser.print_help()

        sys.stdout.write('\nCommands available:\n')
        available_commands = list(set(command_dict.values()))
        available_commands.sort(key=lambda x: x.name)

        indent = 0
        for command in available_commands:
            if command.hidden:
                continue
            length = len(command.name)
            indent = length if indent < len(command.name) else indent

        for command in available_commands:
            if command.hidden:
                continue
            sys.stdout.write('  %-*s  %s\n' % (indent, command.name, command.summary))
        sys.stdout.write('\nFurther information:\n  http://shimehari.hageee.net\n')
        return 0

Command()


def load_command(name):
    full_name = 'shimehari.core.manage.commands.%s' % name
    if full_name in sys.modules:
        return
    try:
        __import__(full_name)
    except ImportError:
        pass


def load_all_commands():
    for name in command_names():
        load_command(name)


def command_names():
    names = set((pkg[1] for pkg in walk_packages(path=commands.__path__)))
    return list(names)
