import inspect
import os.path
from functools import partial

try:
    # Pytest 6.x
    from _pytest.skipping import xfailed_key as evalxfail_key
    from _pytest.skipping import evaluate_xfail_marks as mark_eval
except ImportError:
    # Pytest 5.x
    from _pytest.mark.evaluate import MarkEvaluator
    mark_eval = partial(MarkEvaluator, name="xfail")
    try:
        from _pytest.skipping import evalxfail_key
    except ImportError:
        # And pytest 3-4.x
        evalxfail_key = ""


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


class FailedAssumption(AssertionError):
    pass


class AssumeContextManager(object):
    """Context manager whose objects can be used for *soft-assertions*

    This context manager can be accessed directly through `pytest.assume`.

    Checks the expression, if it's false, add it to the
    list of failed assumptions. Also, add the locals at each failed
    assumption, if showlocals is set.

    When used as a context manager::

        with pytest.assume:
            assert expr, msg

    When used directly, it also provides a return value::

        ret = pytest.assume(expr, msg)

    :param expr: Expression to 'assert' on.
    :param msg: Message to display if the assertion fails.
    :return: True or False, acording to `expr`
    """

    def __init__(self):
        self._enter_from_call = False

    def __enter__(self):
        __tracebackhide__ = True
        self._last_status = None
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        __tracebackhide__ = True
        pretty_locals = None
        entry = None
        tb = None
        stack_level = 2 if self._enter_from_call else 1
        (frame, filename, line, funcname, contextlist) = inspect.stack()[stack_level][0:5]
        # get filename, line, and context
        try:
            filename = os.path.relpath(filename)
        except ValueError:
            pass  # filename is on a different mount than the current dir (Windows)

        context = "" if contextlist is None else contextlist[0].lstrip()

        if exc_type is None:
            # format entry
            entry = u"{filename}:{line}: AssumptionSuccess\n>>\t{context}".format(**locals())
            pytest._hook_assume_pass(lineno=line, entry=entry)

            self._last_status = True
            return True

        elif issubclass(exc_type, AssertionError):
            if exc_val:
                context += "{}: {}\n\n".format(exc_type.__name__, exc_val)

            # format entry
            entry = u"{filename}:{line}: AssumptionFailure\n>>\t{context}".format(**locals())

            # Debatable whether we should display locals for
            # every failed assertion, or just the final one.
            # I'm defaulting to per-assumption, just because vars
            # can easily change between assumptions.
            pretty_locals = [
                "\t%-10s = %s" % (name, saferepr(val)) for name, val in frame.f_locals.items()
            ]

            pytest._hook_assume_fail(lineno=line, entry=entry)
            _FAILED_ASSUMPTIONS.append(Assumption(entry, exc_tb, pretty_locals))

            self._last_status = False
            return True

        else:
            # Another type of exception, let it rise uncaught
            return

    def __call__(self, expr, msg=""):
        __tracebackhide__ = True
        self._enter_from_call = True
        with self:
            if msg:
                assert expr, msg
            else:
                assert expr
        self._enter_from_call = False
        return self._last_status


assume = AssumeContextManager()


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

    # As per pytest documentation: https://docs.pytest.org/en/latest/deprecations.html
    # The pytest.config global object is deprecated. Instead use request.config (via the request fixture)
    # or if you are a plugin author use the pytest_configure(config) hook.
    pytest._hook_assume_fail = config.pluginmanager.hook.pytest_assume_fail
    pytest._hook_assume_pass = config.pluginmanager.hook.pytest_assume_pass
    pytest._hook_assume_summary_report = config.pluginmanager.hook.pytest_assume_summary_report


@pytest.hookimpl(tryfirst=True)
def pytest_assume_fail(lineno, entry):
    pass


@pytest.hookimpl(tryfirst=True)
def pytest_assume_pass(lineno, entry):
    pass


@pytest.hookimpl(tryfirst=True)
def pytest_assume_summary_report(failed_assumptions):
    if getattr(pytest, "_showlocals"):
        content = "".join(x.longrepr() for x in failed_assumptions)
    else:
        content = "".join(x.repr() for x in failed_assumptions)

    return content


def restore_xfail(item):
    # Restore the xfail marker, as it's removed by the strict xfail checking, and will need to be
    # there for later xfail/xpass checking to work.
    if hasattr(item, "_store"):
        item._store[evalxfail_key] = mark_eval(item)
    else:
        item._evalxfail = mark_eval(item)


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_call(item):
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

            content = pytest._hook_assume_summary_report(failed_assumptions=failed_assumptions)

            # Pluggy module returns list for multiple implementation of hooks
            # The user, while implementing custom hook pytest_assume_summary_report, will return "string"
            # Default hook is always present as list element 0
            if len(content) == 1:  # default length
                # Uses default hook
                content = content[0]
            else:
                # User created hook, if any
                content = content[1]

            last_tb = failed_assumptions[-1].tb

            del _FAILED_ASSUMPTIONS[:]
            if outcome and outcome.excinfo:
                # Xfailed test, but with strict=True. This is done via the pytest_pyfunc_call() hook, which
                # is before our hook.
                if "[XPASS(strict)]" in str(outcome.excinfo[1]):
                    restore_xfail(item)
                    raise_(FailedAssumption, FailedAssumption("%s\n%s" % (root_msg, content)), last_tb)
                root_msg = "\nOriginal Failure:\n\n>> %s\n" % repr(outcome.excinfo[1]) + root_msg
                raise_(
                    FailedAssumption,
                    FailedAssumption(root_msg + "\n" + content),
                    outcome.excinfo[2],
                )
            else:
                exc = FailedAssumption(root_msg + "\n" + content)
                # Note: raising here so that we guarantee a failure.
                raise_(FailedAssumption, exc, last_tb)
