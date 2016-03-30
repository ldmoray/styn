#!/usr/bin/python

from pynt import chore


@chore()
def clean():
    """Clean build directory."""

    print("clean")


@chore()
def html():
    """Generate HTML."""

    print("html")


@chore()
def images():
    """Prepare images."""

    print("images")


@chore()
def android():
    """Package Android app."""

    print("android")


@chore()
def ios():
    """Package iOS app."""

    print("ios")


def some_utility_method():
    """Some utility method."""

    print("some utility method")


__DEFAULT__ = ios
