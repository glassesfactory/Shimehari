# -*- coding: utf-8 -*-
#!/usr/bin/env python

from shimehari import renderTemplate, shared
from shimehari.controllers import ApplicationController

import logging


class ChildController(ApplicationController):
    def index(self, *args, **kwargs):
        huge = 'huaaaa'
        return renderTemplate('index.html', huga=huge)

    def show(self, *args, **kwargs):
        return 'response show'
