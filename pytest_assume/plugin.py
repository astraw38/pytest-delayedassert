import inspect
import sys
import os.path
from six import reraise as raise_

import pytest

try:
    from py.io import saferepr
except ImportError:
    saferepr = repr

_FAILED_ASSUMPTIONS = []


class Assumption(object):
    __slots__ = ["entry", "tb", "locals"]

    def __init__(self, entry, tb, locals=None):
        self.entry = entry
        # TODO: trim the TB at init?
        self.tb = tb
        self.locals = locals

    def longrepr(self):
        output = [self.entry, "Locals:"]
        output.extend(self.locals)

        return "\n".join(output)

    def repr(self):
        return self.entry


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
    __tracebackhide__ = True
    pretty_locals = None
    entry = None
    tb = None
    (frame, filename, line, funcname, contextlist) = inspect.stack()[1][0:5]
    # get filename, line, and context
    filename = os.path.relpath(filename)
    context = contextlist[0].lstrip() if not msg else msg

    if not expr:
        # format entry
        entry = u"{filename}:{line}: AssumptionFailure\n>>\t{context}".format(**locals())

        # Debatable whether we should display locals for
        # every failed assertion, or just the final one.
        # I'm defaulting to per-assumption, just because vars
        # can easily change between assumptions.
        pretty_locals = ["\t%-10s = %s" % (name, saferepr(val))
                         for name, val in frame.f_locals.items()]

        try:
            raise FailedAssumption(entry)
        except FailedAssumption:
            exc, _, tb = sys.exc_info()

        pytest._hook_assume_fail(lineno=line, entry=entry)
        _FAILED_ASSUMPTIONS.append(Assumption(entry, tb, pretty_locals))
        return False
    else:
        # format entry
        entry = u"{filename}:{line}: AssumptionSuccess\n>>\t{context}".format(**locals())

        pytest._hook_assume_pass(lineno=line, entry=entry)
        return True

def pytest_addhooks(pluginmanager):
    """ This example assumes the hooks are grouped in the 'hooks' module. """

    from . import hooks
    pluginmanager.add_hookspecs(hooks)

def pytest_configure(config):
    """
    Add tracking lists to the pytest namespace, so we can
    always access it, as well as the 'assume' function itself.

    :return: Dictionary of name: values added to the pytest namespace.
    """
    pytest.assume = assume
    pytest._showlocals = config.getoption("showlocals")

    #As per pytest documentation: https://docs.pytest.org/en/latest/deprecations.html
    #The pytest.config global object is deprecated. Instead use request.config (via the request fixture)
    #or if you are a plugin author use the pytest_configure(config) hook.
    pytest._hook_assume_fail = config.pluginmanager.hook.pytest_assume_fail
    pytest._hook_assume_pass = config.pluginmanager.hook.pytest_assume_pass

@pytest.hookimpl(tryfirst=True)
def pytest_assume_fail(lineno, entry):
    pass

@pytest.hookimpl(tryfirst=True)
def pytest_assume_pass(lineno, entry):
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
        if failed_assumptions:
            failed_count = len(failed_assumptions)
            root_msg = "\n%s Failed Assumptions:\n" % failed_count

            if getattr(pytest, "_showlocals"):
                content = "".join(x.longrepr() for x in failed_assumptions)
            else:
                content = "".join(x.repr() for x in failed_assumptions)

            last_tb = failed_assumptions[-1].tb

            del _FAILED_ASSUMPTIONS[:]
            if outcome and outcome.excinfo:
                root_msg = "\nOriginal Failure:\n\n>> %s\n" % repr(outcome.excinfo[1]) + root_msg
                raise_(FailedAssumption, FailedAssumption(root_msg + "\n" + content), outcome.excinfo[2])
            else:
                exc = FailedAssumption(root_msg + "\n" + content)
                # Note: raising here so that we guarantee a failure.
                raise_(FailedAssumption, exc, last_tb)
