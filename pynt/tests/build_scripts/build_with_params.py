#!/usr/bin/python

from pynt import chore

tasks_run = []


@chore()
def clean(directory='/tmp'):
    tasks_run.append('clean[%s]' % directory)


@chore(clean)
def html():
    tasks_run.append('html')


@chore()
def tests(*test_names):
    tasks_run.append('tests[%s]' % ','.join(test_names))


@chore(clean)
def copy_file(from_, to, fail_on_error='True'):
    tasks_run.append('copy_file[%s,%s,%s]' % (from_, to, fail_on_error))


@chore(clean)
def start_server(port='80', debug='True'):
    tasks_run.append('start_server[%s,%s]' % (port, debug))


@chore(ignore=True)
def ignored(afile, contents):
    tasks_run.append('append_to_file[%s,%s]' % (afile, contents))


@chore(clean, ignored)
def append_to_file(afile, contents):
    tasks_run.append('append_to_file[%s,%s]' % (afile, contents))


@chore(ignored)
def echo(*args, **kwargs):
    args_str = []
    if args:
        args_str.append(','.join(args))
    if kwargs:
        args_str.append(','.join("%s=%s" % (kw, kwargs[kw]) for kw in sorted(kwargs)))

    tasks_run.append('echo[%s]' % ','.join(args_str))
