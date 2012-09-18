# -*- coding: utf-8 -*-
#!/usr/bin/env python

from shimehari import renderTemplate, shared
from shimehari.controllers import ApplicationController

import logging

class TakenokoController(ApplicationController):
	def index(self, *args, **kwargs):
		huge = 'hugaaaan'
		return renderTemplate('index.html',huga=huge)
		# return 'Shimehari GKGKGKGKGKGK!'

	def show(self, *args, **kwargs):
		return 'response show'