import inspect
import os.path
from six import reraise as raise_

import pytest

try:
    from py.io import saferepr
except ImportError:
    saferepr = repr

_FAILED_ASSUMPTIONS = []
_ASSUMPTION_LOCALS = []
global_plugin_mgr = None


class FailedAssumption(Exception):
    pass


def assume(expr, msg=''):
    """
    Checks the expression, if it's false, add it to the
    list of failed assumptions. Also, add the locals at each failed
    assumption, if showlocals is set.

    :param expr: Expression to 'assert' on.
    :param msg: Message to display if the assertion fails.
    :return: None
    """
    if not expr:
        global_plugin_mgr.hook.pytest_assume_fail()
        (frame, filename, line, funcname, contextlist) = inspect.stack()[1][0:5]
        # get filename, line, and context
        filename = os.path.relpath(filename)
        context = contextlist[0].lstrip() if not msg else msg
        # format entry
        entry = u"{filename}:{line}: AssumptionFailure\n>>\t{context}".format(**locals())
        # add entry
        _FAILED_ASSUMPTIONS.append(entry)
        if getattr(pytest, "_showlocals", None):
            # Debatable whether we should display locals for
            # every failed assertion, or just the final one.
            # I'm defaulting to per-assumption, just because vars
            # can easily change between assumptions.
            pretty_locals = ["\t%-10s = %s" % (name, saferepr(val))
                             for name, val in frame.f_locals.items()]
            _ASSUMPTION_LOCALS.append(pretty_locals)
            
        return False
    else:
        global_plugin_mgr.hook.pytest_assume_pass()
        return True

def pytest_addhooks(pluginmanager):
    """ This example assumes the hooks are grouped in the 'hooks' module. """
    from . import hooks

    global global_plugin_mgr

    pluginmanager.add_hookspecs(hooks)
    global_plugin_mgr = pluginmanager

def pytest_configure(config):
    """
    Add tracking lists to the pytest namespace, so we can
    always access it, as well as the 'assume' function itself.

    :return: Dictionary of name: values added to the pytest namespace.
    """
    pytest.assume = assume
    pytest._showlocals = config.getoption("showlocals")

@pytest.hookimpl(tryfirst=True)
def pytest_assume_fail():
    pass
	
@pytest.hookimpl(tryfirst=True)
def pytest_assume_pass():
    pass
	
@pytest.hookimpl(hookwrapper=True)
def pytest_pyfunc_call(pyfuncitem):
    """
    Using pyfunc_call to be as 'close' to the actual call of the test as possible.

    This is executed immediately after the test itself is called.

    Note: I'm not happy with exception handling in here.
    """
    __tracebackhide__ = True
    outcome = None
    try:
        outcome = yield
    finally:
        failed_assumptions = _FAILED_ASSUMPTIONS
        assumption_locals = _ASSUMPTION_LOCALS
        if failed_assumptions:
            failed_count = len(failed_assumptions)
            root_msg = "\n%s Failed Assumptions:\n" % failed_count
            if assumption_locals:
                assume_data = zip(failed_assumptions, assumption_locals)
                longrepr = ["{0}\nLocals:\n{1}\n\n".format(assumption, "\n".join(flocals))
                            for assumption, flocals in assume_data]
            else:
                longrepr = ["\n\n".join(failed_assumptions)]

            del _FAILED_ASSUMPTIONS[:]
            del _ASSUMPTION_LOCALS[:]
            if outcome and outcome.excinfo:
                root_msg = "\nOriginal Failure: \n>> %s\n" % repr(outcome.excinfo[1]) + root_msg
                raise_(FailedAssumption, FailedAssumption(root_msg + "".join(longrepr)), outcome.excinfo[2])
            else:
                raise FailedAssumption(root_msg + "".join(longrepr))
