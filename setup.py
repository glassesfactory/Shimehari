#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import Command, setup
from shimehari import VERSION, AUTHOR

class runAudit(Command):
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        pass


setup(
    name='Shimehari',
    version=VERSION,
    url='https://github.com/glassesfactory/Shimehari',
    license='BSD',
    author=AUTHOR,
    author_email='megane@glasses-factory.net',
    description='middle framework based on Flask, Werkzeug, Jinja2 ',
    packages=['shimehari','shimehari.core', 'shimehari.template', 'shimehari.core.conf','shimehari.core.conf.app_template',
                'shimehari.core.conf.app_template.controllers','shimehari.core.conf.app_template.models',
                'shimehari.template.jinja2',
                'shimehari.core.manage','shimehari.core.manage.commands'],
    scripts=['shimehari/core/conf/shimehari'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Werkzeug>=0.7',
        'Jinja2>=2.4'
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    cmdclass={'audit':runAudit},
    test_suite='shimehari.testsuite.suite'
)