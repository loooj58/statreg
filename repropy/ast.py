#!/usr/bin/python
"""
Tools for building AST for evauation
"""

from abc import ABC,abstractmethod
import struct
import hashlib

from .hashes import merklize

# ----------------------------------------------------------------

class Context(object):
    """
    Context for the analysis. It provides access to
    content-addressable storage
    """
    def __init__(self, meta, store="."):
        self.meta  = meta
        self.store = "."

    def call(self, action, *args, **kwargs):
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
        return FunctionNode(self, action(self.meta), args, kwargs)
    
    def has_hash(self, h):
        """
        Hash given hash in store
        """
        return False

    def fetch(self, h):
        """
        Retrieve value from store
        """
        raise Exception("Not implemented")

    def store(self, h, val):
        """
        Put value into store
        """
        pass

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
        #
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
        Evaluate node value
        """
        # Check whether value is cached
        h = self.hash()
        if self.ctx.has_hash(h):
            return self.ctx.fetch(h)
        # Evaluate arguments for the action
        args   = [ a.value()  for a   in self.args   ]
        kwargs = { k: v.value for k,v in self.kwargs }
        return self.action(*args, **kwargs)

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
