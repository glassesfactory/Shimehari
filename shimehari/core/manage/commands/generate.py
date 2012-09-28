#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
===============================
    Shimehari.core.manage.commands.generate
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    アプリケーションモジュールを新たに作成する generate コマンド

    各コマンドモジュールは共通インターフェースとして
    Command クラスを持ちます。

===============================
"""
import os
import sys
import shutil

from optparse import make_option

import shimehari
from shimehari.core.exceptions import CommandError
from shimehari.core.helpers import importFromString
from shimehari.core.manage import CreatableCommand
from shimehari.helpers import getEnviron
from shimehari.configuration import ConfigManager, Config


u"""
===============================
    ::pkg:: Shimehari.core.manage.commands.generate
    Command
    ~~~~~~~

    コマンドの実装

===============================
"""


class Command(CreatableCommand):
    name = 'generate'
    summary = 'Generate Shimehari Modules'
    usage = "Usage: %prog MODULE_NAME [OPTIONS]"

    option_list = CreatableCommand.option_list + (
        make_option('--path', '-p', action='store', type='string', dest='path', help='generating target path'),
    )

    def __init__(self):
        super(Command, self).__init__()

    def handle(self, moduleType, name, *args, **options):
        if not moduleType == 'controller':
            raise CommandError('ない')

        path = options.get('path')
        if path is None:
            currentPath = os.getcwd()
            try:
                importFromString('config')
            except:
                sys.path.append(os.getcwd())
                try:
                    importFromString('config')
                except ImportError:
                    raise CommandError('config file is not found...')
            config = ConfigManager.getConfig(getEnviron())
            path = os.path.join(currentPath, config['APP_DIRECTORY'], config['CONTROLLER_DIRECTORY'])

        if not os.path.isdir(path):
            raise CommandError('Given path is invalid')

        ctrlTemplate = os.path.join(shimehari.__path__[0], 'core', 'conf', 'controller_template.org.py')

        name, filename = self.filenameValidation(path, name)
        newPath = os.path.join(path, filename)

        self.readAndCreateFileWithRename(ctrlTemplate, newPath, name)

    def filenameValidation(self, path, name):
        if name.endswith(('.pyc', '.pyo', '.py.class')):
            raise CommandError('invalid name....')
        if not name.endswith('.py'):
            filename = name + '.py'
        else:
            filename = name
            name = name.replace('.py', '')

        name = self.checkDirectory(path, name)

        import re
        if re.search(r"\W", name) or re.match(r"\d", name[0]):
            raise CommandError('file name is invalid')
        name = name[0].upper() + name[1:]
        return name, filename

    def checkDirectory(self, path, name):
        sep = None
        if '.' in name:
            sep = '.'
        elif '/' in name:
            sep = '/'
        else:
            pass
        names = [name]
        if sep is not None:
            names = name.split(sep)
        name = names.pop()
        d = "/".join(names)
        td = os.path.join(path, d)
        if not os.path.isdir(td):
            try:
                os.makedirs(td)
            except (IOError, OSError), e:
                raise CommandError('invaild name... %s' % e)
        return name

    def readAndCreateFileWithRename(self, old, new, name):
        u"""指定されたディレクトリからテンプレートファイルを読み込み
        新たに生成したい指定ディレクトリへファイルを生成します。

        :param old: テンプレートファイルのパス
        :param new: 生成したいディレクトリへのパスとファイル名
        :param name: 変更したいクラス名
        """
        if os.path.exists(new):
            raise CommandError('Controller already exists.')

        with open(old, 'r') as template:
            content = template.read()
            
            if '%s' in content:
                content = content % name
                content = content[3:]
                content = content[:len(content) - 4]
                
        with open(new, 'w') as newFile:
            newFile.write(content)
        sys.stdout.write("Genarating New Controller: %s\n" % new)

        try:
            shutil.copymode(old, new)
            self.toWritable(new)
        except OSError:
            sys.stderr.write('can not setting permission')

Command()
