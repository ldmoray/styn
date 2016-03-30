from pynt import chore


@chore()
def clean():
    pass


# Should be marked as task.
def html():
    pass


# References a non task.
@chore(clean, html)
def android():
    pass
