#!/usr/bin/python
"""
"""
from dataclasses import is_dataclass, fields
import inspect
import hashlib

from .hashes import merklize_rec


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


class Meta(object):
    """
    Wrapper class which actually uses metadata
    """
    def __init__(self, meta, fun):
        acc = hashlib.sha256()
        acc.update( fun.__module__.encode('utf-8') )
        acc.update( fun.__name__.encode('utf-8') )
        # Introspect function and construct metadata object from
        # complete metadata
        pars      = inspect.getfullargspec(fun)
        ty        = pars.annotations[pars.args[0]]
        self.meta = instantiate(ty, meta)
        merklize_rec(acc, self.meta)
        self.h    = acc.digest()
        self.fun  = fun

    def __call__(self, *args, **kwargs) :
        return self.fun(self.meta, *args, **kwargs)

    def hash(self):
        return self.h
