#!/usr/bin/python
from pynt import chore


@chore()
def clean():
    """Clean build directory."""
    print('Cleaning build directory...')


@chore(clean)
def html(target='.'):
    """Generate HTML."""
    print('Generating HTML in directory "%s"' % target)


@chore(clean, ignore=True)
def images():
    """Prepare images."""
    print('Preparing images...')


@chore(html, images)
def start_server(server='localhost', port='80'):
    """Start the server"""
    print('Starting server at %s:%s' % (server, port))


@chore(start_server)  # Depends on task with all optional params
def stop_server():
    print('Stopping server....')


@chore()
def copy_file(src, dest):
    print('Copying from %s to %s' % (src, dest))


@chore()
def echo(*args, **kwargs):
    print(args)
    print(kwargs)


@chore()
def error_task():
    print "this should fail with an error"
    raise IOError


# Default task (if specified) is run when no task is specified in the command line
# make sure you define the variable __DEFAULT__ after the task is defined
# A good convention is to define it at the end of the module
# __DEFAULT__ is an optional member

__DEFAULT__ = start_server
