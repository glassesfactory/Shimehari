# -*- coding: utf-8 -*-
#!/usr/bin/env python


u"""
======================================
    Shimehari Command Line Manager
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    ochoko is Shimehari Command Line Manager.

    commands example....

    :new <app_name> [options]...
        create new Shimehari App.

    :generate <controller_name> [options]....
        generate new controller

        ::Options

        -p, [--path]:
            path shitei


    and see more --help

======================================
"""

import os,sys

if __name__ == '__main__':
    from shimehari.core.manage import executeFromCommandLine
    executeFromCommandLine(sys.argv)