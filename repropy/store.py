#!/usr/bin/python
"""
"""
import base64
import os
import pickle

class Store(object):
    """
    Hash-adressable storage for python object
    """
    def __init__(self,path):
        self.path = path
        os.makedirs(path, exist_ok=True)

    def fetch(self,h):
        """
        Fetch value from store. On success returns (object,True) or
        (None,False) otherwise
        """
        nm = self._path(h)
        try:
            with open(nm,'rb') as h:
                return (pickle.load(h), True)
        except FileNotFoundError:
            return (None, False)

    def store(self, h, val):
        """
        Store value
        """
        nm = self._path(h)
        # NOTE: We try to serialize object before we create file!
        #       Otherwise unserializable object will leave empty file
        #       in store
        bs = pickle.dumps(val)
        with open(nm,'wb') as h:
            h.write(bs)

    def _path(self, h):
        s  = base64.urlsafe_b64encode(h).decode('utf-8').replace('=', '')
        return os.path.join(self.path, s)
