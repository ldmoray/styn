from pynt import chore

tasks_run = []

@chore()
def clean():
    tasks_run.append("clean")

@chore(clean)
def html():
    'Generate HTML.'
    tasks_run.append("html")

@chore(clean, ignore=True)
def images():
    """Prepare images.

    Should be ignored."""

    raise Exception("This task should have been ignored.")

@chore(clean, html, images)
def android():
    "Package Android app."

    tasks_run.append('android')

