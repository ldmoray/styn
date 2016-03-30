from pynt import chore


@chore()
def clean():
    """Clean build directory."""

    print("clean")

@chore(clean)
def html():
    """Generate HTML."""
    
    print("html")

@chore(clean)
def images():
    """Prepare images."""

    print("images")

@chore(clean, html, images)
def android():
    """Package Android app."""

    print("android")

@chore(clean, html, images)
def ios():
    """Package iOS app."""

    print("ios")
    
def some_utility_method():
    """Some utility method."""

    print("some utility method")
