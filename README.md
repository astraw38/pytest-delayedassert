# pytest-assume
[![Build Status](https://travis-ci.org/astraw38/pytest-assume.svg?branch=master)](https://travis-ci.org/astraw38/pytest-assume)

A pytest plugin that allows multiple failures per test

Forked from Brian Okken's work with ['pytest-expect'](https://github.com/okken/pytest-expect), there are a few changes/improvements:


1. Showlocals support
2. Global usage support (Does not need a fixture)
3. Output tweaking

## Installation

  `pip install git+https://github.com/astraw38/pytest-assume.git`  
  or   
  `pip install pytest-assume`  

## Usage

Sample Usage:
```python
import pytest
    
@pytest.mark.parametrize(('x', 'y'), [(1, 1), (1, 0), (0, 1)])
def test_simple_assume(x, y):
    pytest.assume(x == y)
    pytest.assume(True)
    pytest.assume(False)
```        
        
    ======================================== FAILURES =========================================
    _________________________________ test_simple_assume[1-1] _________________________________
    >    pytest.assume(False)
    test_assume.py:7
 
    y          = 1
    x          = 1
    ----------------------------------------
    Failed Assumptions:1
    _________________________________ test_simple_assume[1-0] _________________________________
    >    pytest.assume(x == y)
    test_assume.py:5

    y          = 0
    x          = 1
    >    pytest.assume(False)
    test_assume.py:7

    y          = 0
    x          = 1
    ----------------------------------------
    Failed Assumptions:2
    _________________________________ test_simple_assume[0-1] _________________________________
    >    pytest.assume(x == y)
    test_assume.py:5

    y          = 1
    x          = 0
    >    pytest.assume(False)
    test_assume.py:7

    y          = 1
    x          = 0
    ----------------------------------------
    Failed Assumptions:2
    ================================ 3 failed in 0.02 seconds =================================

`pytest.assume` can also be used as a context manager around plain assertions:

```python
import pytest
from pytest import assume
    
@pytest.mark.parametrize(('x', 'y'), [(1, 1), (1, 0), (0, 1)])
def test_simple_assume(x, y):
    with assume: assert x == y
    with assume: assert True
    with assume: assert False
``` 

Notice that **there should be only one assertion per *with* block**. This, for instance, will not
work as the second and third assertions will never be executed if the first one fails:

```python
import pytest
    
@pytest.mark.parametrize(('x', 'y'), [(1, 1), (1, 0), (0, 1)])
def test_simple_assume(x, y):
    with pytest.assume:
        assert x == y
        assert True
        assert False
``` 
