#!/usr/bin/python
# -*- coding: utf-8 -*-

import collections
import cPickle

import bsddb3

def _dumps(o):
    return cPickle.dumps(o, -1).encode('zlib')

def _loads(o):
    return cPickle.loads(o.decode('zlib'))


def open(dbenv, filename, dbname=None, flags=bsddb3.db.DB_CREATE, mode=0660, txn=None):
    d = DBList(dbenv)
    d.open(filename, dbname, bsddb3.db.DB_RECNO, flags, mode, txn)
    return d


class DBList(collections.MutableSequence):
    def __init__(self, dbenv):
        self.db = bsddb3.db.DB(dbenv)
        self._closed = True


    def __del__(self):
        self.close()


    def __repr__(self):
        if self._closed:
            return '<DBList @ 0x%x - closed>' % (id(self))
        else:
            return repr(list(self))


    def __getitem__(self, index):
        try:
            data = self.db[index+1]
            return _loads(data)
        except:
            raise IndexError


    def __setitem__(self, index, value):
        data = _dumps(value)
        self.db[index+1] = data


    def __delitem__(self, index):
        del self.db[index+1]


    def __len__(self):
        return len(self.db)


    def insert(self, index, value):
        pass


    def append(self, value, txn=None):
        data = _dumps(value)
        return self.db.append(data, txn)


    def open(self, *args, **kwargs):
        self.db.open(*args, **kwargs)
        self._closed = False


    def close(self, *args, **kwargs):
        self.db.close(*args, **kwargs)
        self._closed = True
