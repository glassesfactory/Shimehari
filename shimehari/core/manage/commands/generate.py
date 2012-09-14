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
    help = ("Generate Shimehari Modules")
    option_list = CreatableCommand.option_list + (
            make_option('--path', '-p', action='store', type='string', dest='path', help='generating target path'),
            make_option('--namespace', '-ns', action='store', type='string', dest='prefix', help='prefix generetiong target path')
        )

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

        prefix = options.get('prefix')
        if prefix is not None:
            path = prefix + path
            #うーむ
            #os.path.join(path,prefix)

        ctrlTemplate = os.path.join(shimehari.__path__[0], 'core','conf', 'controller_template.org.py')
        
        name, filename = self.filenameValidation(name)
        newPath = os.path.join(path,filename)

        self.readAndCreateFileWithRename(ctrlTemplate, newPath, name)



    def filenameValidation(self, name):
        if name.endswith(('.pyc','.pyo', '.py.class')):
            raise CommandError('invalid name....')
        if not name.endswith('.py'):
            filename = name + '.py'
        else:
            filename = name
            name = name.replace('.py', '')

        import re
        if re.search(r"\W", name) or re.match(r"\d", name[0]):
            raise CommandError('file name is invalid')
        name = name[0].upper() + name[1:]
        return name, filename



    u"""-----------------------------
        ::pkg:: Shimehari.core.manage.commands.generate.Command
        readAndCreateFileWithRename
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~

        指定されたディレクトリからテンプレートファイルを読み込み
        新たに生成したい指定ディレクトリへファイルを生成します。
        [args]
            :old テンプレートファイルのパス
            :new 生成したいディレクトリへのパスとファイル名
            :name 変更したいクラス名
    ------------------------------"""
    def readAndCreateFileWithRename(self, old, new, name):
        if os.path.exists(new):
            raise CommandError('Controller already exists.')

        with open(old, 'r') as template:
            content = template.read()
            if '%s' in content:
                content = content % name
                content = content[3:]
                content = content[:len(content) -3]
        with open(new, 'w') as newFile:
            newFile.write(content)
        sys.stdout.write("Genarating New Controller: %s\n" % new)

        try:
            shutil.copymode(old,new)
            self.toWritable(new)
        except OSError:
            sys.stderr.write('can not setting permission')
