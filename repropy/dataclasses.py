#!/usr/bin/python
"""
"""
from   dataclasses import is_dataclass, fields, MISSING
import copy
import hashlib
import inspect
import marshal
import typing
import types
from .hashes import merklize_rec

## ----------------------------------------------------------------

def instantiate(cls, dct):
    """
    Create dataclass from dictionary. All unused elements from
    dictionary are discarded
    """
    # Dataclasses are instantiated from dictionaries
    if is_dataclass(cls) :
        par = {}
        for f in fields(cls):
            nm = f.name
            ty = f.type
            # Skip instantiation of missing fields with default value
            if not (nm in dct) and f.default != MISSING:
                continue
            # Otherwise instantiate value from dict
            par[nm] = instantiate(ty, dct.get(nm))
        return cls(**par)
    # Lists are instantiated from iterables
    if getattr(cls, "__origin__", None) is list :
        tyArg = cls.__args__[0]
        return [instantiate(tyArg, d) for d in dct]
    # Unions.
    if getattr(cls, "__origin__", None) is typing.Union :
        for ty in cls.__args__:
            # Dataclasses require tags which are names of data type
            if is_dataclass(ty) and isinstance(dct, dict):
                if ty.__name__ == dct.get("%tag") :
                    return instantiate(ty, dct)
                else:
                    continue
            # None always succeeds. Note that Optional[a] ~ Union[a,NoneType]
            # so this approach works
            if ty is type(None):
                return None
            # Otherwise pick first match
            if issubclass(type(dct), ty):
                return dct
        raise InstantiationError("Cannot instantiate %s from %s" % (cls,dct))
    # All else fails
    if issubclass(type(dct), cls):
        return dct
    raise InstantiationError("Cannot instantiate %s from %s" % (cls,dct))

class InstantiationError(Exception):
    def __init__(self, str):
        super().__init__(str)


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

def hash_function(acc, fun):
    acc.update( fun.__module__.encode('utf-8') )
    acc.update( fun.__name__.encode('utf-8') )
    # If function has code field - use if
    code = getattr(fun, "__code__",None)
    if code is not None:
        acc.update( marshal.dumps(fun.__code__) )
        return
    # Otherwise it's class. Deal with it. Or try
    for k,v in sorted(fun.__dict__.items()):
        if k in ["__doc__", "__dict__","__weakref__","__module__"]:
            continue
        acc.update( k.encode('utf-8') )
        if isinstance(v, types.FunctionType):
            acc.update(marshal.dumps(v.__code__))
        else:
            merklize_rec(acc, v)



class NoMeta(object):
    """
    Wrapper class for functions which does not make use of metadata
    """
    def __init__(self, fun):
        acc = hashlib.sha256()
        hash_function(acc, fun)
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
        hash_function(acc, fun)
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
