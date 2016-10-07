#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys

from setuptools import setup


trove_classifiers=[
    "Development Status :: 5 - Production/Stable",
    "Environment :: Console",
    "License :: OSI Approved :: GNU General Public License (GPL)",
    "Intended Audience :: End Users/Desktop",
    "Intended Audience :: System Administrators",
    "Operating System :: OS Independent",
    "Natural Language :: English",
    "Programming Language :: Python",
    "Topic :: Utilities",
    "Topic :: System :: Filesystems",
    "Topic :: System :: Distributed Computing",
]


setup(
    name="lafs",
    description='frontend for the Tahoe-LAFS secure, decentralized, fault-tolerant file store',
    long_description="FIXME",#open('README.rst', 'rU').read(),
    author='the Tahoe-LAFS project',
    author_email='tahoe-dev@tahoe-lafs.org',
    url='https://tahoe-lafs.org/',
    license='GNU GPL',
    package_dir = {'':'.'},
    packages=['lafs'],
    classifiers=trove_classifiers,
    install_requires=[
        'click',
        'twisted',
        #'wormhole',
        #'-e https://github.com/warner/magic-wormhole/archive/master.zip#egg=magic-wormhole',
        #'-e git+https://github.com/warner/magic-wormhole.git',
    ],
    entry_points={
        'console_scripts': [
            'lafs = lafs.cli:lafs'
        ]
    },
)
