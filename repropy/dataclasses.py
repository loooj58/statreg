#!/usr/bin/python
"""
"""
from dataclasses import is_dataclass, fields


def instantiate(cls, dct):
    """
    Create dataclass from dictionary. All unused elements from
    dictionary are discarded
    """
    if not is_dataclass(cls):
        raise Exception(str(cls) + " is not a dataclass")
    # Build parameters
    par = {}
    for f in fields(cls):
        nm = f.name
        ty = f.type
        if is_dataclass(ty) :
            par[nm] = instantiate(ty, dct[nm])
        else:
            par[nm] = dct[nm]
    return cls(**par)
