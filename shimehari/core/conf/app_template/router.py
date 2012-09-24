#!/usr/bin/env python
# -*- cofing: utf-8 -*-

from shimehari import Router, Resource
from controllers import IndexController

#
# You can routing like Rails style.
#
# from shimehari.routing import RESTfulRouter
# appRoutes = RESTfulRouter([
#    Resource(IndexController,root=True),
#    Resource(SomeOtherController),
#    Resource(SomethingElseController, expect=['edit', 'destroy'])
#])


appRoutes = Router([
    Resource(IndexController, root=True)
])

#
# You can routing like werkzeug style.
#
# from shimehari import BasicRouter
# appRoutes = BasicRouter([
#    {'/': IndexController.list},
#    {'/hoge': SomeOtherController.list},
#    {'/hoge/<int:id>': SomeOtherController.show}
#])
