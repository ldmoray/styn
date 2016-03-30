"""
Lightweight Python Build Tool for Celery Users

"""

import inspect
import argparse
import logging
import os
from os import path
import re
import imp
import sys
from styn import __version__

_CREDIT_LINE = "Powered by styn %s - A Lightweight Python Build Tool for Celery Users." % __version__
_LOGGING_FORMAT = "[ %(name)s - %(message)s ]"
_CHORE_PATTERN = re.compile("^([^\[]+)(\[([^\]]*)\])?$")
# "^([^\[]+)(\[([^\],=]*(,[^\],=]+)*(,[^\],=]+=[^\],=]+)*)\])?$"


def build(args):
    """
    Build the specified module with specified arguments.
    
    @type args: list of arguments
    """
    # Build the command line.
    parser = _create_parser()

    # No args passed.
    # if not args: #todo: execute default chore.
    #    parser.print_help()
    #    print("\n\n"+_CREDIT_LINE)
    #    exit
    # Parse arguments.
    args = parser.parse_args(args)

    if args.version:
        print('styn %s' % __version__)
        sys.exit(0)

    # load build file as a module
    if not path.isfile(args.file):
        print("Build file '%s' does not exist. Please specify a build file\n" % args.file)
        parser.print_help()
        sys.exit(1)

    module = imp.load_source(path.splitext(path.basename(args.file))[0], args.file)

    # Run chore and all its dependencies.
    if args.list_chores:
        print_chores(module, args.file)
    elif not args.chores:
        if not _run_default_chore(module):
            parser.print_help()
            print("\n")
            print_chores(module, args.file)
    else:
        _run_from_chore_names(module, args.chores)


def print_chores(module, build_file):
    # Get all chores.
    chores = _get_chores(module)

    # Build chore_list to describe the chores.
    chore_list = "Chores in build build_file %s:" % build_file
    name_width = _get_max_name_length(module) + 4
    chore_help_format = "\n  {0:<%s} {1: ^10} {2}" % name_width
    default = _get_default_chore(module)
    for chore in sorted(chores, key=lambda chore: chore.name):
        attributes = []
        if chore.ignored:
            attributes.append('Ignored')
        if default and chore.name == default.name:
            attributes.append('Default')

        chore_list += chore_help_format.format(chore.name,
                                               ('[' + ', '.join(attributes) + ']')
                                               if attributes else '',
                                               chore.doc)
    print(chore_list + "\n\n" + _CREDIT_LINE)


def _get_default_chore(module):
    matching_chores = [chore for name, chore in inspect.getmembers(module, Chore.is_chore) if name == "__DEFAULT__"]
    if matching_chores:
        return matching_chores[0]


def _run_default_chore(module):
    default_chore = _get_default_chore(module)
    if not default_chore:
        return False
    _run(module, _get_logger(module), default_chore, set())
    return True


def _run_from_chore_names(module, chore_names):
    """
    @type module: module
    @type chore_names: list string
    @param chore_names: Chore names, exactly corresponds to function name.
    """
    # Create logger.
    logger = _get_logger(module)
    all_tasks = _get_chores(module)
    completed_tasks = set([])
    for chore_name in chore_names:
        chore, args, kwargs = _get_chore(module, chore_name, all_tasks)
        _run(module, logger, chore, completed_tasks, True, args, kwargs)


def _get_chore(module, name, chores):
    # Get all chores.
    match = _CHORE_PATTERN.match(name)
    if not match:
        raise Exception("Invalid chore argument %s" % name)
    chore_name, _, args_str = match.groups()

    args, kwargs = _parse_args(args_str)
    if hasattr(module, chore_name):
        return getattr(module, chore_name), args, kwargs
    matching_chores = [chore for chore in chores if chore.name.startswith(chore_name)]

    if not matching_chores:
        raise Exception("Invalid chore '%s'. Chore should be one of %s" %
                        (name, ', '.join([chore.name for chore in chores])))
    if len(matching_chores) == 1:
        return matching_chores[0], args, kwargs
    raise Exception("Conflicting matches %s for chore %s" %
                    (', '.join([chore.name for chore in matching_chores]), chore_name))


def _parse_args(args_str):
    args = []
    kwargs = {}
    if not args_str:
        return args, kwargs
    arg_parts = args_str.split(",")

    for i, part in enumerate(arg_parts):
        if "=" in part:
            key, value = [_str.strip() for _str in part.split("=")]
            if key in kwargs:
                raise Exception("duplicate keyword argument %s" % part)
            kwargs[key] = value
        else:
            if len(kwargs) > 0:
                raise Exception("Non keyword arg %s cannot follows a keyword arg %s"
                                % (part, arg_parts[i - 1]))
            args.append(part.strip())
    return args, kwargs


def _run(module, logger, chore, completed_chores, from_command_line=False, args=None, kwargs=None):
    """
    @type module: module
    @type logger: Logger
    @type chore: Chore
    @type completed_chores: set Chore
    @rtype: set Chore
    @return: Updated set of completed tasks after satisfying all dependencies.
    """
    # Satisfy dependencies recursively. Maintain set of completed tasks so each
    # chore is only performed once.
    for dependency in chore.dependencies:
        completed_chores = _run(module, logger, dependency, completed_chores)

    # Perform current chore, if need to.
    if from_command_line or chore not in completed_chores:

        if chore.ignored:

            logger.info("Ignoring chore \"%s\"" % chore.name)

        else:

            logger.info("Starting chore \"%s\"" % chore.name)

            try:
                # Run chore.
                chore(*(args or []), **(kwargs or {}))
            except:
                logger.critical("Error in chore \"%s\"" % chore.name)
                logger.critical("Aborting build")
                raise

            logger.info("Completed chore \"%s\"" % chore.name)

        completed_chores.add(chore)

    return completed_chores


def _create_parser():
    """
    @rtype: argparse.ArgumentParser
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("chores", help="perform specified chore and all its dependencies",
                        metavar="chore", nargs='*')
    parser.add_argument('-l', '--list-chores', help="List the chores",
                        action='store_true')
    parser.add_argument('-v', '--version',
                        help="Display the version information",
                        action='store_true')
    parser.add_argument('-f', '--file',
                        help="Build file to read the chores from. 'build.py' is default value assumed if this argument is unspecified",
                        metavar="file", default="build.py")

    return parser


# Abbreviate for convenience.
# chore = _TaskDecorator
def chore(*dependencies, **options):
    for i, dependency in enumerate(dependencies):
        if not Chore.is_chore(dependency):
            if inspect.isfunction(dependency):
                # Throw error specific to the most likely form of misuse.
                if i == 0:
                    raise Exception("Replace use of @chore with @chore().")
                else:
                    raise Exception("%s is not a chore. Each dependency should be a chore." % dependency)
            else:
                raise Exception("%s is not a chore." % dependency)

    def decorator(fn):
        return Chore(fn, dependencies, options)

    return decorator


class Chore(object):
    def __init__(self, func, dependencies, options):
        """
        @type func: 0-ary function
        @type dependencies: list of Chore objects
        """
        self.func = func
        self.name = func.__name__
        self.doc = inspect.getdoc(func) or ''
        self.dependencies = dependencies
        self.ignored = bool(options.get('ignore', False))

    def __call__(self, *args, **kwargs):
        self.func.__call__(*args, **kwargs)

    @classmethod
    def is_chore(cls, obj):
        """
        Returns true if an object is a build chore.
        @type obj: Object
        """
        return isinstance(obj, cls)


def _get_chores(module):
    """
    Returns all functions marked as tasks.
    
    @type module: module
    """
    # Get all functions that are marked as chores and pull out the chore object
    # from each (name,value) pair.
    return set(member[1] for member in inspect.getmembers(module, Chore.is_chore))


def _get_max_name_length(module):
    """
    Returns the length of the longest chore name.
    
    @type module: module
    """
    return max([len(chore.name) for chore in _get_chores(module)])


def _get_logger(module):
    """
    @type module: module
    @rtype: logging.Logger
    """

    # Create Logger
    logger = logging.getLogger(os.path.basename(module.__file__))
    logger.setLevel(logging.DEBUG)

    # Create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # Create formatter
    formatter = logging.Formatter(_LOGGING_FORMAT)

    # Add formatter to ch
    ch.setFormatter(formatter)

    # Add ch to logger
    logger.addHandler(ch)

    return logger


def main():
    build(sys.argv[1:])
