# Standard library imports
import unittest
from doctest import DocTestSuite

# Zope imports
import zope.component.testing


def setUp(test):
    #zope.component.testing.setUp(test)
    #zope.component.provideAdapter(RecipeReadFile)
    pass

suites = (
    DocTestSuite('quills.remoteblogging.browser.metaweblogapi',
                 setUp=zope.component.testing.setUp,
                 tearDown=zope.component.testing.tearDown),
        )

def test_suite():
    return unittest.TestSuite(suites)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')