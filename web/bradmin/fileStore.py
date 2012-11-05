""" Implements a simple filestore 'database' """
""" keys are treated as paths and file names """
""" this is meant to run on unix like systems """
""" so keys like foo/bar/item """
""" will be stored in directory foo, directory bar, item. """
""" if you run it on windows, you'll probably get a filename like 'foo/bar/item' """

import os

def makedirs(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == 17: # file exists
            pass
        else:
            raise e    

class fileStore(object):
    def __init__(self, root):
        """ root is the root location on the file system where the store resides """
        """ e.g. db = fileStore('/var/cache/bradmin/db') """
        self.root = root
        makedirs(self.root)
    def get(self, key):
        """ return the value of the key """
        """ raise an error if not found """
        fullpath = os.path.join(self.root, key)
        f = open(fullpath)
        return f.read()

    def store(self, key, value, cas=0):
        """ store a value with an optional cas check """
        """ if cas is non-zero, the cas value must match the key cas """
        """ internally, for a filestore the cas is just the last modified time of a file """
        """ (is this ok? should be the fastest but breaks down if the BR doesn't have good time """
        if cas != 0:
            raise NotImplementedError
        fullpath = os.path.join(self.root, key)
        path = os.path.dirname(fullpath)
        filename = os.path.basename(key)
        makedirs(path)
        outfile = open(fullpath, 'w+b')
        outfile.write(value)

