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
                raise CommandError('コンフィグファイルが見当たりません')
            config = ConfigManager.getConfig(getEnviron())
            path = os.path.join(currentPath, config['APP_DIRECTORY'], config['CONTROLLER_DIRECTORY'])

        if not os.path.isdir(path):
           raise CommandError('パスが不正です')

        ctrlTemplate = os.path.join(shimehari.__path__[0], 'core','conf', 'controller_template.py')
        
        name, filename = self.filenameValidation(name)
        newPath = os.path.join(path,filename)

        self.readAndCreateFileWithRename(ctrlTemplate, newPath, name)



    def filenameValidation(self, name):
        if name.endswith(('.pyc','.pyo', '.py.class')):
            raise CommandError('おかしな名前使うな')
        if not name.endswith('.py'):
            filename = name + '.py'
        else:
            filename = name
            name = name.replace('.py', '')

        import re
        if re.search(r"\W", name) or re.match(r"\d", name[0]):
            raise CommandError('指定されたファイル名が不正です')
        name[0].upper() + name[1:]
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
            raise CommandError('もうあるぽよ')

        with open(old, 'r') as template:
            content = template.read()
            if '%s' in content:
                content = content % name
        with open(new, 'w') as newFile:
            newFile.write(content)
        sys.stdout.write("Genarating New Controller: %s\n" % new)

        try:
            shutil.copymode(old,new)
            self.toWritable(new)
        except OSError:
            sys.stderr.write('パーミッション設定できんかった')
