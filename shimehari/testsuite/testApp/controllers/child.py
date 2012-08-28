#!/usr/bin/env python
# -*- coding: utf-8 -*-

from shimehari import Request, Response, ApplicationController

class ChildController(ApplicationController):
    def __init__(self, name):
        ApplicationController.__init__(self,name)

    #Create your controller here.

    def index(self, *args, **kwargs):
        return 'child index'

    def show(self, *args, **kwargs):
        return 'show'

    def edit(self, *args, **kwargs):
        return 'edit child'

    def new(self, *args, **kwargs):
        return 'new child'

    def create(self, *args, **kwargs):
        return 'create child'

    def update(self, *args, **kwargs):
        return 'update child'

    def destroy(self, *args, **kwargs):
        return 'destroy child'
