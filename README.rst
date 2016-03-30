|Build Status|

A styn of Python build.
=======================

`Lenny Morayniss <https://github.com/ldmoray>`__

Features
--------

-  Easy to learn.
-  Build tasks are just python functions.
-  Manages dependencies between tasks.
-  Automatically generates a command line interface.
-  Rake style param passing to tasks
-  Supports python 2.7 and python 3.x
-  Tasks are called chores.
-  Works with Celery.

Installation
------------

You can install styn from the Python Package Index (PyPI) or from
source.

Using pip

.. code:: bash

    $ pip install styn

Using easy\_install

.. code:: bash

    $ easy_install styn

Example
-------

The build script is written in pure Python and styn takes care of
managing any dependencies between tasks and generating a command line
interface.

Writing build tasks is really simple, all you need to know is the @task
decorator. Tasks are just regular Python functions marked with the
``@task()`` decorator. Dependencies are specified with ``@task()`` too.
Tasks can be ignored with the ``@task(ignore=True)``. Disabling a task
is an useful feature to have in situations where you have one task that
a lot of other tasks depend on and you want to quickly remove it from
the dependency chains of all the dependent tasks.

**build.py**
------------

.. code:: python


    #!/usr/bin/python

    import sys
    from styn import chore

    @chore()
    def clean():
        '''Clean build directory.'''
        print 'Cleaning build directory...'

    @chore(clean)
    def html(target='.'):
        '''Generate HTML.'''
        print 'Generating HTML in directory "%s"' %  target

    @chore(clean, ignore=True)
    def images():
        '''Prepare images.'''
        print 'Preparing images...'

    @chore(html,images)
    def start_server(server='localhost', port = '80'):
        '''Start the server'''
        print 'Starting server at %s:%s' % (server, port)

    @chore(start_server) #Depends on task with all optional params
    def stop_server():
        print 'Stopping server....'

    @chore()
    def copy_file(src, dest):
        print 'Copying from %s to %s' % (src, dest)

    @chore()
    def echo(*args,**kwargs):
        print args
        print kwargs
        
    # Default task (if specified) is run when no task is specified in the command line
    # make sure you define the variable __DEFAULT__ after the task is defined
    # A good convention is to define it at the end of the module
    # __DEFAULT__ is an optional member

    __DEFAULT__=start_server

**Running styn chores**
-----------------------

The command line interface and help is automatically generated. Task
descriptions are extracted from function docstrings.

.. code:: bash

    $ styn -h
    usage: styn [-h] [-l] [-v] [-f file] [task [task ...]]

    positional arguments:
      task                  perform specified task and all its dependencies

    optional arguments:
      -h, --help            show this help message and exit
      -l, --list-tasks      List the tasks
      -v, --version         Display the version information
      -f file, --file file  Build file to read the tasks from. Default is
                            'build.py'

.. code:: bash

    $ styn -l
    Tasks in build file ./build.py:
      clean                       Clean build directory.
      copy_file                   
      echo                        
      html                        Generate HTML.
      images           [Ignored]  Prepare images.
      start_server     [Default]  Start the server
      stop_server                 

    Powered by styn - A Lightweight Python Build Tool for Celery Users.

styn takes care of dependencies between tasks. In the following case
start\_server depends on clean, html and image generation (image task is
ignored).

.. code:: bash

    $ styn #Runs the default task start_server. It does exactly what "styn start_server" would do.
    [ example.py - Starting task "clean" ]
    Cleaning build directory...
    [ example.py - Completed task "clean" ]
    [ example.py - Starting task "html" ]
    Generating HTML in directory "."
    [ example.py - Completed task "html" ]
    [ example.py - Ignoring task "images" ]
    [ example.py - Starting task "start_server" ]
    Starting server at localhost:80
    [ example.py - Completed task "start_server" ]

The first few characters of the task name is enough to execute the task,
as long as the partial name is unambiguous. You can specify multiple
tasks to run in the commandline. Again the dependencies are taken taken
care of.

.. code:: bash

    $ styn cle ht cl
    [ example.py - Starting task "clean" ]
    Cleaning build directory...
    [ example.py - Completed task "clean" ]
    [ example.py - Starting task "html" ]
    Generating HTML in directory "."
    [ example.py - Completed task "html" ]
    [ example.py - Starting task "clean" ]
    Cleaning build directory...
    [ example.py - Completed task "clean" ]

The 'html' task dependency 'clean' is run only once. But clean can be
explicitly run again later.

styn tasks can accept parameters from commandline.

.. code:: bash

    $ styn "copy_file[/path/to/foo, path_to_bar]"
    [ example.py - Starting task "clean" ]
    Cleaning build directory...
    [ example.py - Completed task "clean" ]
    [ example.py - Starting task "copy_file" ]
    Copying from /path/to/foo to path_to_bar
    [ example.py - Completed task "copy_file" ]

styn can also accept keyword arguments.

.. code:: bash

    $ styn start[port=8888]
    [ example.py - Starting task "clean" ]
    Cleaning build directory...
    [ example.py - Completed task "clean" ]
    [ example.py - Starting task "html" ]
    Generating HTML in directory "."
    [ example.py - Completed task "html" ]
    [ example.py - Ignoring task "images" ]
    [ example.py - Starting task "start_server" ]
    Starting server at localhost:8888
    [ example.py - Completed task "start_server" ]
        
    $ styn echo[hello,world,foo=bar,blah=123]
    [ example.py - Starting task "echo" ]
    ('hello', 'world')
    {'blah': '123', 'foo': 'bar'}
    [ example.py - Completed task "echo" ]

**Organizing build scripts**
----------------------------

You can break up your build files into modules and simple import them
into your main build file.

.. code:: python

    from deploy_tasks import *
    from test_tasks import functional_tests, report_coverage

Contributors/Contributing
-------------------------

-  Raghunandan Rao - styn is preceded by and forked from
   `pynt <https://github.com/rags/pynt>`__, which was created by
   `Raghunandan Rao <https://github.com/rags>`__.
-  Calum J. Eadie - pynt is preceded by and forked from
   `microbuild <https://github.com/CalumJEadie/microbuild>`__, which was
   created by `Calum J. Eadie <https://github.com/CalumJEadie>`__.

If you want to make changes the repo is at
https://github.com/ldmoray/styn. You will need
`pytest <http://www.pytest.org>`__ to run the tests

.. code:: bash

    $ ./b t

It will be great if you can raise a `pull
request <https://help.github.com/articles/using-pull-requests>`__ once
you are done.

*If you find any bugs or need new features please raise a ticket in the
`issues section <https://github.com/ldmoray/styn/issues>`__ of the
github repo.*

Really, this is just a downstream fork to rename "tasks" to "chores"
though.

License
-------

pynt is licensed under a `MIT
license <http://opensource.org/licenses/MIT>`__

.. |Build Status| image:: https://travis-ci.org/ldmoray/styn.svg?branch=master
   :target: https://travis-ci.org/ldmoray/styn
