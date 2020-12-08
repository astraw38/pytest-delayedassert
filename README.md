# pytest-assume
[Build Status](https://github.com/astraw38/pytest-assume/workflows/Tox%20Unittest/badge.svg)

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
Output:
```        
   ================================== FAILURES ===================================
    ___________________________ test_simple_assume[1-1] ___________________________
    
    tp = <class 'pytest_assume.plugin.FailedAssumption'>, value = None, tb = None
    
        def reraise(tp, value, tb=None):
            try:
                if value is None:
                    value = tp()
                if value.__traceback__ is not tb:
    >               raise value.with_traceback(tb)
    E               pytest_assume.plugin.FailedAssumption: 
    E               1 Failed Assumptions:
    E               
    E               test_simple_fail.py:7: AssumptionFailure
    E               >>	pytest.assume(False)
    E               AssertionError: assert False
    
    C:\Users\astraw\Projects\pytest-assume\venv\lib\site-packages\six.py:692: FailedAssumption
    ___________________________ test_simple_assume[1-0] ___________________________
    
    tp = <class 'pytest_assume.plugin.FailedAssumption'>, value = None, tb = None
    
        def reraise(tp, value, tb=None):
            try:
                if value is None:
                    value = tp()
                if value.__traceback__ is not tb:
    >               raise value.with_traceback(tb)
    E               pytest_assume.plugin.FailedAssumption: 
    E               2 Failed Assumptions:
    E               
    E               test_simple_fail.py:5: AssumptionFailure
    E               >>	pytest.assume(x == y)
    E               AssertionError: assert False
    E               
    E               test_simple_fail.py:7: AssumptionFailure
    E               >>	pytest.assume(False)
    E               AssertionError: assert False
    
    C:\Users\astraw\Projects\pytest-assume\venv\lib\site-packages\six.py:692: FailedAssumption
    ___________________________ test_simple_assume[0-1] ___________________________
    
    tp = <class 'pytest_assume.plugin.FailedAssumption'>, value = None, tb = None
    
        def reraise(tp, value, tb=None):
            try:
                if value is None:
                    value = tp()
                if value.__traceback__ is not tb:
    >               raise value.with_traceback(tb)
    E               pytest_assume.plugin.FailedAssumption: 
    E               2 Failed Assumptions:
    E               
    E               test_simple_fail.py:5: AssumptionFailure
    E               >>	pytest.assume(x == y)
    E               AssertionError: assert False
    E               
    E               test_simple_fail.py:7: AssumptionFailure
    E               >>	pytest.assume(False)
    E               AssertionError: assert False
    
    C:\Users\astraw\Projects\pytest-assume\venv\lib\site-packages\six.py:692: FailedAssumption
    ========================== 3 failed in 0.25 seconds ===========================
```

### Context manager

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

Notice that **there should be only one assertion per *with* block**. This, for instance, will not fully verify all
assertions if the first one fails:

```python
import pytest
    
@pytest.mark.parametrize(('x', 'y'), [(1, 1), (1, 0), (0, 1)])
def test_simple_assume(x, y):
    with pytest.assume:
        assert x == y
        assert True
        assert False
``` 
