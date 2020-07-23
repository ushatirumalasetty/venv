"""
Created on 20/11/16

@author: revanth.g
"""


def f7(seq):
    # TODO: supports only primitive data types should extend to objects
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def remove_duplicates(list_obj, preserve_order=False):
    # TODO: supports only primitive data types should extend to objects
    if not preserve_order:
        return list(set(list_obj))
    else:
        return f7(list_obj)
