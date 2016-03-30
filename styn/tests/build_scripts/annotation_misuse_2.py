from styn import chore


@chore()
def clean():
    pass


# Should be marked as chore.
def html():
    pass


# References a non chore.
@chore(clean, html)
def android():
    pass
