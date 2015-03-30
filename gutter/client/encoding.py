# -*- coding: utf-8 -*-

from __future__ import absolute_import

# External Libraries
from durabledict.encoding import PickleEncoding
import jsonpickle as pickle


class JsonPickleEncoding(PickleEncoding):
    @staticmethod
    def encode(data):
        return pickle.dumps(data)

    @staticmethod
    def decode(data):
        try:
            return pickle.loads(data)
        except Exception:
            return PickleEncoding.decode(data)
