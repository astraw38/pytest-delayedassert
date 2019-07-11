import pytest

#Hooks definition
def pytest_assume_pass(lineno, entry):
    print ("Inside assume_pass hook")
    print ("lineno = %s, entry = %s" % (lineno, entry))
def pytest_assume_fail(lineno, entry):
    print ("Inside assume_fail hook")
    print ("lineno = %s, entry = %s" % (lineno, entry))
