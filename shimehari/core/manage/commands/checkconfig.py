#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from optparse import make_option

from shimehari.core.exceptions import CommandError
from shimehari.core.manage import AbstractCommand
from shimehari.core.helpers import importFromString
from shimehari.configuration import ConfigManager, Config

class Command(AbstractCommand):
	help = ("Check Your Shimehari Application Configration")
	option_list = AbstractCommand.option_list + (
            make_option('--env', '-e', action='store', type='string', dest='environ', help='get config environ'),
        )

	def handle(self, *args, **options):
		try:
			importFromString('config')
		except ImportError:
			sys.path.append(os.getcwd())
			try:
				importFromString('config')
			except ImportError:
				raise CommandError(u'コンフィグファイルが見当たりません')

		env = options.get('env')
		if env is None:
			env = 'development'
		
		sys.stdout.write('\nYour Shimehari App Current Config.\n\n')
		sys.stdout.write('-------------------------------------------------\n')
		sys.stdout.write(ConfigManager.getConfig(env).dump())
		sys.stdout.write('\n')


