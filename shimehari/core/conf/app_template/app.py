#!/usr/bin/env python
# -*- coding: utf-8 -*-

from shimehari import Shimehari

app = Shimehari(__name__)

if __name__ == '__main__':
    app.drink()

#
# You can routing like Rails style.
#
#app.router = RESTfulRouter(
#        Resource(IndexController,root=True),
#        Resource(SomeOtherController),
#        Resource(SomethingElseController, expect=['edit', 'destroy'])
#    )

#
# You can routing like werkzeug style.
# 
# from shimehari import BasicRouter
# app.router = BasicRouter(
#        {'/':IndexController.list},
#        {'/hoge':SomeOtherController.list},
#        {'/hoge/<int:id>':SomeOtherController.show}
#    )
