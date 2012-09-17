#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
===============================
    Shimehari.core.manage.commands.create
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    アプリケーションを新たに作成する create コマンド
    
    各コマンドモジュールは共通インターフェースとして
    Command クラスを持ちます。
    
===============================
"""

import os
import sys
import random
import errno
import shutil
from optparse import make_option

import shimehari
from shimehari.core.manage import CreatableCommand
from shimehari.core.helpers import importFromString
from shimehari.core.exceptions import CommandError

debugFormat = "('-' * 80 + '\\n' + '%(levelname)s in %(module)s [%(pathname)s:%(lineno)d]:\\n' + '%(message)s\\n' + '-' * 80)" 

outputFormat = "('%(asctime)s %(levelname)s in %(module)s [%(pathname)s:%(lineno)d]:\\n' + '%(message)s\\n' + '-' * 80)"

u"""
===============================
    ::pkg:: Shimehari.core.manage.commands.create
    Command
    ~~~~~~~
    コマンドの実装
    
===============================
"""
class Command(CreatableCommand):
    help = ("Create Shimehari Application.")
    option_list = CreatableCommand.option_list + (
            make_option('--path', '-p', action='store', type='string', dest='path', help='target create path'),
            make_option('--template', '-t', action='store', type='string', dest='template', help='using project tempalte')
        )

    def handle(self, appDir='app', *args, **options):
        try:
            importFromString(appDir)
        except ImportError:
            pass
        else:
            raise CommandError('%s mou aru' % appDir)

        path = options.get('path')
        if path is None:
            appRootDir = os.path.join(os.getcwd(), appDir)
            try:
                os.makedirs(appRootDir)
            except OSError, error:
                if error.errno == errno.EEXIST:
                    msg = '%s is already exists' % appRootDir
                else:
                    msg = error
                raise CommandError(msg)
        else:
            appRootDir = os.path.abspath(os.path.expanduser(path))
            if not os.path.exists(appRootDir):
                raise CommandError("auau")

        template = options.get('template')
        if template is None:
            appTemplateDir = os.path.join(shimehari.__path__[0], 'core','conf', 'app_template')
        else:
            appTemplateDir = template

        prefixLen = len(appTemplateDir) + 1

        for root, dirs, files in os.walk(appTemplateDir):
            pathRest = root[prefixLen:]
            relativeDir = pathRest.replace('app_name','app')
            if relativeDir:
                targetDir = os.path.join(appRootDir,relativeDir)
                if not os.path.exists(targetDir):
                    os.mkdir(targetDir)

            for dirname in dirs[:]:
                if dirname.startswith('.'):
                    dirs.remove(dirname)

            for filename in files[:]:
                if filename.endswith(('.pyo','.pyc','.py.class')):
                    continue
                oldPath = os.path.join(root, filename)
                newPath = os.path.join(appRootDir, relativeDir, filename.replace('app_name', 'app'))

                self.readAndCreateFile(oldPath, newPath)

        #ここどうすっかな
        self.createDirectory(appRootDir, 'views')
        self.createDirectory(appRootDir, 'assets')
        self.createDirectory(appRootDir, 'log')

        #generate config file
        confOrgPath = os.path.join(shimehari.__path__[0], 'core', 'conf','config.org.py')
        newConfPath = os.path.join(os.getcwd(), 'config.py')
        self.readAndCreateFileWithRename(confOrgPath, newConfPath, 
                                            (appDir, appDir, debugFormat, outputFormat))
        
        sys.stdout.write("New App Create Complete. enjoy!\n")



    u"""-----------------------------
        ::pkg:: Shimehari.core.manage.commands.create.Command
        readAndCreateFile
        ~~~~~~~~~~~~~~~~~

        指定されたディレクトリからテンプレートファイルを読み込み
        新たに生成したい指定ディレクトリへファイルを生成します。
        [args]
            :old テンプレートファイルのパス
            :new 生成したいディレクトリへのパスとファイル名
    ------------------------------"""
    def readAndCreateFile(self, old, new):
        if os.path.exists(new):
            raise CommandError('already... %s' % new)

        with open(old, 'r') as template:
            content = template.read()
        with open(new, 'w') as newFile:
            newFile.write(content)
        sys.stdout.write(u"Creating: %s\n" % new)

        try:
            shutil.copymode(old,new)
            self.toWritable(new)
        except OSError:
            sys.stderr.write('permission error')


    def readAndCreateFileWithRename(self, old, new, name):
        if os.path.exists(new):
            raise CommandError('Controller already exists.')

        with open(old, 'r') as template:
            content = template.read()
            if '%s' in content:
                content = content % name
        with open(new, 'w') as newFile:
            newFile.write(content)
        sys.stdout.write("Creating: %s\n" % new)

        try:
            shutil.copymode(old,new)
            self.toWritable(new)
        except OSError:
            sys.stderr.write('can not setting permission')

    def createDirectory(self, rootDir, dirname):
        targetName = os.path.join(rootDir, dirname)
        if not os.path.exists(targetName):
            os.mkdir(targetName)
            sys.stdout.write("Creating: %s\n" % targetName) 





    
