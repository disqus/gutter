# -*- coding: utf-8 -*-

from __future__ import absolute_import

# Standard Library
import pickle as old_pickle

# External Libraries
import jsonpickle as pickle


class JsonPickleEncoding(object):
    @staticmethod
    def encode(data):
        return pickle.dumps(data)

    @staticmethod
    def decode(data):
        try:
            return pickle.loads(data)
        except Exception:
            return old_pickle.loads(data)
