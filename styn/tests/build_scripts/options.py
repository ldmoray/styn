from styn import chore

chores_run = []


@chore()
def clean():
    chores_run.append("clean")


@chore(clean)
def html():
    """Generate HTML."""
    chores_run.append("html")


@chore(clean, ignore=True)
def images():
    """Prepare images.

    Should be ignored."""

    raise Exception("This chore should have been ignored.")


@chore(clean, html, images)
def android():
    """Package Android app."""

    chores_run.append('android')
