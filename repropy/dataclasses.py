#!/usr/bin/python
"""
"""
from dataclasses import is_dataclass, fields
import hashlib

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


def no_meta(fun):
    def wrapper(meta):
        return NoMeta(fun)
    return wrapper

class NoMeta(object):
    """
    Wrapper class for functions which does not make use of metadata
    """
    def __init__(self, fun):
        acc = hashlib.sha256()
        acc.update( fun.__module__.encode('utf-8') )
        acc.update( fun.__name__.encode('utf-8') )
        self.h   = acc.digest()
        self.fun = fun

    def __call__(self, *args, **kwargs):
        return self.fun(*args, **kwargs)

    def hash(self):
        return self.h
