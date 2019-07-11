import pytest

#Hooks definition
def pytest_assume_pass():
    print ("Inside assume_pass hook")
def pytest_assume_fail():
    print ("Inside assume_fail hook")
