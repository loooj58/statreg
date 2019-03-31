#!/usr/bin/python
"""
Tools for building AST for evauation
"""

from abc import ABC,abstractmethod
import struct
import hashlib

from .hashes      import merklize
from .            import store
from .dataclasses import WithMeta, NoMeta


# ----------------------------------------------------------------

class Context(object):
    """
    Context for the analysis. It provides access to
    content-addressable storage
    """
    def __init__(self, meta, store_dir="./store"):
        self.meta  = meta
        self.store = store.Store(store_dir)

    def call0(self, action, *args,
              meta_cheap=False, meta_path=None,
              **kwargs):
        """
        Call function which doesnt receive any metadata
        """
        return self._call_raw(NoMeta(action), *args,
                              meta_cheap=meta_cheap,
                              **kwargs)

    def call(self, action, *args,
             meta_cheap=False, meta_path=None,
             **kwargs):
        """
        Call function which receives metadata as first parameter
        """
        meta = self.meta
        if meta_path is not None:
            for k in meta_path:
                meta = meta[k]
        return self._call_raw(WithMeta(meta, action), *args,
                              meta_cheap=meta_cheap,
                              **kwargs)

    def _call_raw(self, action, *args,
                  meta_cheap=False, **kwargs):
        """
        Create delayed function call. Action is assumed to be
        """
        def to_arg(a) :
            if isinstance(a, Node) :
                return a
            else:
                return Literal(a)
        args   = [ to_arg(a) for a in args ]
        kwargs = { k : to_arg(v) for k,v in kwargs.items() }
        node   = FunctionNode(self, action, args, kwargs)
        node.cheap = meta_cheap
        return node



## ================================================================
## Nodes in the AST
## ================================================================

class Node(ABC):
    """
    Base class for the node in AST for program for analysis
    """
    @abstractmethod
    def value(self):
        """
        Evaluate node and return its value
        """
        pass

    @abstractmethod
    def hash(self):
        """
        Calculate hash of the node
        """
        pass

class FunctionNode(Node):
    """
    Node which wraps evaluation of function
    """
    def __init__(self, ctx, action, args=None, kwargs=None):
        """
        """
        self.ctx    = ctx
        self.action = action
        self.args   = [] if args is None else args
        self.kwargs = {} if args is None else kwargs
        # Build Merkle tree from parameters
        acc = hashlib.sha256()
        acc.update( self.action.hash() )
        for a in args:
            acc.update( a.hash() )
        for k,v in sorted(kwargs):
            acc.update( k.encode('utf-8') )
            acc.update( v.hash() )
        self.h = acc.digest()

    def value(self):
        """
        Evaluate node (or fetch value from cache if possible)
        """
        # Check whether value is cached
        if not self.cheap:
            h        = self.hash()
            (val,ok) = self.ctx.store.fetch(h)
            if ok:
                return val
        # Evaluate arguments for the action
        args   = [ a.value()  for a   in self.args   ]
        kwargs = { k: v.value for k,v in self.kwargs }
        val    = self.action(*args, **kwargs)
        self.ctx.store.store(h, val)
        return val

    def hash(self):
        return self.h


class Literal(Node):
    """
    Node which holds literal value and thus doesn't need any
    computations
    """
    def __init__(self, val):
        if isinstance(val, Node):
            raise Exception("Node instance cannot be literal")
        self.val = val
        self.h   = merklize(val)

    def value(self):
        return self.val

    def hash(self):
        return self.h

    def __str__(self):
        return "Literal(%s)" % str(self.val)

    def __repr__(self):
        return "Literal(%s)" % repr(self.val)
