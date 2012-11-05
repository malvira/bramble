import os, subprocess

import logging
log = logging.getLogger(__name__)

from fileStore import *

if __name__ == "__main__":
    root = '/tmp/db'
    path = 'foo/bar/item'
    fullpath = os.path.join(root, path)
    print fullpath
    db = fileStore(root)

    print "test store"
    value = 'foofoofoo'
    db.store(path,value)
    if value == db.get(path):
        print "OK!"
    else:
        print "Failed."

    print "test CAS not implemented"
    try:
        db.store('foo/bar/item','foofoofoo',123)
    except NotImplementedError:
        print "OK!"



