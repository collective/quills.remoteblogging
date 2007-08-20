# ********************************************
# class     CaselessDict
# purpose   emulate a normal Python dictionary
#           but with keys which can accept the
#           lower() method (typically strings).
#           Accesses to the dictionary are
#           case-insensitive but keys returned
#           from the dictionary are always in
#           the original case.
# Taken from a comment by Chris Hobbs (2005/07/16) @
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66315
# ********************************************


class CaselessDict:

    def __init__(self,inDict=None):
        """Constructor: takes conventional dictionary as input (or nothing)
        """
        self.dict = {}
        if inDict != None:
            for key in inDict:
                k = key.lower()
                self.dict[k] = (key, inDict[key])
        self.keyList = self.dict.keys()
        return

    def __iter__(self):
        self.iterPosition = 0
        return(self)

    def next(self):
        if self.iterPosition >= len(self.keyList):
            raise StopIteration
        x = self.dict[self.keyList[self.iterPosition]][0]
        self.iterPosition += 1
        return x

    def __getitem__(self, key):
        k = key.lower()
        return self.dict[k][1]

    def __setitem__(self, key, value):
        k = key.lower()
        self.dict[k] = (key, value)
        self.keyList = self.dict.keys()

    def has_key(self, key):
        k = key.lower()
        return k in self.keyList

    def __len__(self):
        return len(self.dict)

    def keys(self):
        return [v[0] for v in self.dict.values()]

    def values(self):
        return [v[1] for v in self.dict.values()]

    def items(self):
        return self.dict.values()

    def __contains__(self, item):
        return self.dict.has_key(item.lower())

    def __repr__(self):
        items = ", ".join([("%r: %r" % (k,v)) for k,v in self.items()])
        return "{%s}" % items

    def __str__(self):
        return repr(self)

    def get(self, key, alt=None):
        if self.has_key(key):
            return self.__getitem__(key)
        return alt