#!/usr/bin/python

from pynt.tests.build_scripts.simple import *
from pynt.tests.build_scripts import build_with_params

tasks_run = []


@chore()
def local_task():
    tasks_run.append('local_task')


@chore(clean, build_with_params.html, local_task)
def task_with_imported_dependencies():
    tasks_run.append('task_with_imported_dependencies')


__DEFAULT__ = task_with_imported_dependencies
