#!/usr/bin/python
"""
"""
from   dataclasses import is_dataclass, fields, MISSING
import copy
import hashlib
import inspect
import marshal
import typing
from .hashes import merklize_rec

## ----------------------------------------------------------------

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
        if not (nm in dct) and f.default != MISSING:
            continue
        if is_dataclass(ty) :
            par[nm] = instantiate(ty, dct[nm])
        elif getattr(ty, "__origin__", None) is list :
            tyArg = ty.__args__[0]
            par[nm] = [instantiate(tyArg, d) for d in dct[nm]]
        else:
            par[nm] = dct[nm]
    return cls(**par)

class Meta(dict):
    """
    Extension of dictionary which allows sensisble merging of metadata
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __add__(self, other):
        def to_meta(val):
            if isinstance(val, Meta):
                return val
            if isinstance(val, dict):
                return Meta(**val)
            raise Exception("Cannot convert " + str(type(val)) + " Meta")
        tagA = self.get("%tag")
        tagB = other.get("%tag")
        if tagA != tagB:
            raise Exception("Tag mismatch: %s + %s" % (tagA,tagB))
        new = copy.copy(self)
        for k,v in other.items() :
            if k in new :
                a = new[k]
                if isinstance(a, dict) or isinstance(v, dict):
                    new[k] = to_meta(a) + to_meta(v)
                else:
                    new[k] = v
            else:
                new[k] = v
        return new

class Tagged(Meta):
    """
    Metadata with tag attached
    """
    def __init__(self, tag, **kwargs):
        self["%tag"] = tag
        super().__init__(**kwargs)

################################################################

class NoMeta(object):
    """
    Wrapper class for functions which does not make use of metadata
    """
    def __init__(self, fun):
        acc = hashlib.sha256()
        acc.update( fun.__module__.encode('utf-8') )
        acc.update( fun.__name__.encode('utf-8') )
        acc.update( marshal.dumps(fun.__code__) )
        self.h   = acc.digest()
        self.fun = fun

    def __call__(self, *args, **kwargs):
        return self.fun(*args, **kwargs)

    def hash(self):
        return self.h


class WithMeta(object):
    """
    Wrapper class which actually uses metadata
    """
    def __init__(self, meta, fun):
        acc = hashlib.sha256()
        acc.update( fun.__module__.encode('utf-8') )
        acc.update( fun.__name__.encode('utf-8') )
        acc.update( marshal.dumps(fun.__code__) )
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
