# Do not modify carelessly
# This is used by mcl.py to do
# execution and parsing of scripts.
# In a concurrent manner!

# HANDLE WITH INTENSE CARE

# Contributors:
#     Darren Chase Papa

# INCOMPLETE

from itertools import chain, zip_longest

def interleave_lists(list1, list2):
    return list(chain(*zip_longest(list1, list2, fillvalue=None)))
