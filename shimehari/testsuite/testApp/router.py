#!/usr/bin/env python
# -*- cofing: utf-8 -*-

from shimehari import Router, Resource
from controllers import IndexController, HogeController, NinjaController, TakenokoController

appRoutes = Router([
		Resource(IndexController, root=True),
		Resource(HogeController, [
				Resource(NinjaController),
				Resource(TakenokoController)
			])
	])