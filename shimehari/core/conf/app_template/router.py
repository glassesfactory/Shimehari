#!/usr/bin/env python
# -*- cofing: utf-8 -*-

from shimehari import Router, Resource
from controllers import IndexController

appRoutes = Router([
		Resource(IndexController, root=True)
	])