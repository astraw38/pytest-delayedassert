#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open("VERSION") as f:
    VERSION = f.read().strip()

setup(
    name="pytest-assume",
    packages=["pytest_assume"],
    version=VERSION,
    description="A pytest plugin that allows multiple failures per test",
    author="Brian Okken/Ashley Straw",
    author_email="as.fireflash38@gmail.com",
    maintainer="Ashley Straw",
    maintainer_email="as.fireflash38@gmail.com",
    license="MIT",
    keywords=["testing", "pytest", "assert"],
    install_requires=["pytest>=2.7"],
    download_url="https://github.com/astraw38/pytest-assume/tarball/{}".format(VERSION),
    url="https://github.com/astraw38/pytest-assume",
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    # the following makes a plugin available to py.test
    entry_points={"pytest11": ["assume = pytest_assume.plugin"]},
)
