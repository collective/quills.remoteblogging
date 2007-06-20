# ********************************************
# class     caselessDict
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

if __name__ == '__main__':
    foundError = False

    # firstly create an empty caselessDict

    x = caselessDict()
    x['frEd'] = 76
    x['jOe'] = 92
    x['bERT'] = 54
    x['Bert'] = 53
    if x['bert'] != 53:
        print "Error 1"
        foundError = True
    shouldBe = [ 'Bert', 'jOe', 'frEd' ]
    for key in x:
        if not key in shouldBe:
            print "Error 2"
            foundError = True
        else:
            shouldBe.remove(key)
    if len(shouldBe) != 0:
        print "Error 2a"
        foundError = True
    if not 'frEd' in x:
        print "Error 3"
        foundError = True
    if not 'fRed' in x:
        print "Error 4"
        foundError = True
    if 'fReda' in x:
        print "Error 5"
        foundError = True
    y = x.keys()
    if len(y) != 3:
        print "Error 6"
        foundError = True
    for yy in y:
        if (yy != 'Bert') and (yy != 'jOe') and (yy != 'frEd'):
            print "Error 7"
            foundError = True
    if x['FRED'] != 76:
        print "Error 8"
        foundError = True
    if x['joe'] != 92:
        print "Error 9"
        foundError = True

    # then create a caselessDict from an existing dictionary

    y = { 'frEd' : 76, 'jOe' : 92, 'Bert' : 53 }
    x = caselessDict(y)
    if x['bert'] != 53:
        print "Error 10"
        foundError = True
    shouldBe = [ 'Bert', 'jOe', 'frEd' ]
    for key in x:
        if not key in shouldBe:
            print "Error 11"
            foundError = True
        else:
            shouldBe.remove(key)
    if len(shouldBe) != 0:
        print "Error 11a"
        foundError = True
    if not 'frEd' in x:
        print "Error 3"
        foundError = True
    if not 'fRed' in x:
        print "Error 12"
        foundError = True
    y = x.keys()
    if len(y) != 3:
        print "Error 13"
        foundError = True
    for yy in y:
        if (yy != 'Bert') and (yy != 'jOe') and (yy != 'frEd'):
            print "Error 14"
            foundError = True
    if x['FRED'] != 76:
        print "Error 15"
        foundError = True
    if x['joe'] != 92:
        print "Error 16"
        foundError = True
    if foundError == False:
        print "No errors found"