#!/usr/bin/env python
# -*- coding: utf-8 -*-

from shimehari import request, Response, ApplicationController


class IndexController(ApplicationController):
    def __init__(self, name):
        ApplicationController.__init__(self, name)

    #Create your controller here.

    def index(self, *args, **kwargs):
        return Response('Drink Shimehari!')

    def show(self, *args, **kwargs):
        return Response('write show action code...')

    def edit(self, *args, **kwargs):
        return Response('write edit action code...')

    def new(self, *args, **kwargs):
        return Response('write new action code...')

    def create(self, *args, **kwargs):
        return Response('write create action code...')

    def update(self, *args, **kwargs):
        return Response('write update action code...')

    def destroy(self, *args, **kwargs):
        return Response('write destroy action code...')
