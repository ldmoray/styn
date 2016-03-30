#!/usr/bin/python

import subprocess
from styn import chore


@chore()
def apidoc():
    """
    Generate API documentation using epydoc.
    """
    subprocess.call(["epydoc", "--config", "epydoc.config"])


@chore()
def test(*args):
    """
    Run unit tests.
    """
    subprocess.call(["py.test"] + list(args))
    # subprocess.call(["py.test-3.3"] + list(args))


@chore()
def generate_rst():
    subprocess.call(['pandoc', '-f', 'markdown', '-t', 'rst', '-o', 'README.rst', 'README.md'])


@chore(generate_rst)
def upload():
    subprocess.call(['ssh-add', '~/.ssh/id_rsa'])
    subprocess.call(['python', 'setup.py', 'sdist', 'bdist_wininst', 'upload'])


__DEFAULT__ = test
