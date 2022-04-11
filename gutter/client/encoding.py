# -*- coding: utf-8 -*-

from __future__ import absolute_import

# External Libraries
from durabledict.encoding import PickleEncoding
import jsonpickle as pickle


class JsonPickleEncoding(PickleEncoding):

    ENCODING = 'utf-8'

    @staticmethod
    def encode(data):
        json_string = pickle.dumps(data)
        return json_string.encode(JsonPickleEncoding.ENCODING)

    @staticmethod
    def decode(data):
        try:
            json_string = data.decode(JsonPickleEncoding.ENCODING)
            return pickle.loads(json_string)
        except Exception:
            return PickleEncoding.decode(data)


class KeyEncoderProxy:
    """
    Helps to ensure that keys are encoded and decoded.

    This is mainly useful on Python3 where we use text values as the key but on
    some storages like redis we can only store byte values. Without a
    consistent encoding switches cannot be found again, because the returned
    keys are `bytes` objects instead of `str` objects.
    """

    def __init__(self, storage, encoding='utf-8'):
        self._encoding = encoding
        self._storage = storage

    def __setitem__(self, key, val):
        key = key.encode(self._encoding)
        self._storage[key] = val

    def __delitem__(self, key):
        key = key.encode(self._encoding)
        del self._storage[key]

    def __getitem__(self, key):
        key = key.encode(self._encoding)
        return self._storage[key]

    def __contains__(self, key):
        key = key.encode(self._encoding)
        return key in self._storage

    def items(self):
        return (
            (key.decode(self._encoding), val)
            for key, val in self._storage.items())

    def keys(self):
        return (
            key.decode(self._encoding)
            for key in self._storage.keys())
