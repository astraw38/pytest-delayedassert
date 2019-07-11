import pytest


def test1():
    ret1 = pytest.assume(1==1)
    print ("Retval for first assume = %s" % ret1)
    print ("first assumption complete")
    ret2 = pytest.assume(1==2)
    print ("Retval for second assume = %s" % ret2)
    print ("Second assumption complete")
