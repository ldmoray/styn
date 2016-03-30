#!/usr/bin/python

from styn.tests.build_scripts.simple import *
from styn.tests.build_scripts import build_with_params

chores_run = []


@chore()
def local_chore():
    chores_run.append('local_chore')


@chore(clean, build_with_params.html, local_chore)
def chore_with_imported_dependencies():
    chores_run.append('chore_with_imported_dependencies')


__DEFAULT__ = chore_with_imported_dependencies
