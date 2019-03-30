#!/usr/bin/python
"""
Hashing of plain data types

Hopefully there's better way to do this
"""

import struct
import hashlib
from dataclasses import fields, is_dataclass

def merklize(x):
    """
    Calculate hash of value
    """
    acc = hashlib.sha256()
    merklize_rec(acc, x)
    return acc.digest()

def merklize_rec(acc, x):
    """
    Hash given value. Hash is constructed incrementally using given
    accumulator from hashlib
    """
    ty = type(x)
    acc.update( ty.__module__.encode('utf-8') )
    acc.update( ty.__name__.encode('utf-8') )
    if is_dataclass(ty) :
        for nm in sorted([ f.name for f in fields(ty) ]):
            acc.update(nm.encode('utf-8'))
            merklize_rec(acc, x.__dict__[nm])
    else:
        lookup[ty](acc, x)

def hashing_bs(to_bs):
    "Compute hash of value using given serialization function"
    return lambda acc, x: acc.update(to_bs(x))

def hashing_list(acc, xs):
    "Hash list"
    for x in xs:
        merklize_rec(acc, x)

def hashing_dict(acc, xs):
    "Hash dictionary"
    for k,v in sorted(xs.items()):
        merklize_rec(k)
        merklize_rec(v)

# Lookup table or hashing algorithms
lookup = {
    bytearray: hashing_bs(lambda x: x),
    bool:      hashing_bs(lambda b: struct.pack('b', b)),
    int:       hashing_bs(lambda i: struct.pack('l', i)),
    float:     hashing_bs(lambda x: struct.pack('d', x)),
    str:       hashing_bs(lambda s: s.encode('utf-8')),
    # Containers
    list:      hashing_list,
    dict:      hashing_dict,
    }
