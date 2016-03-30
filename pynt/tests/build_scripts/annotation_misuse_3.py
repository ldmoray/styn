from pynt import chore

@chore()
def clean():
    pass
    
# Referring to clean by name rather than reference.
@chore(1234)
def html():
    pass
