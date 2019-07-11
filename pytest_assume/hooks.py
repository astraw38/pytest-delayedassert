def pytest_assume_fail(lineno, entry):
    """
    Hook to manipulate user-defined data in-case of assumption failure.
    lineno: Line in the code from where asumption failed.
    entry: The assumption failure message generated from assume() call
    """
    pass
def pytest_assume_pass(lineno, entry):
    """
    Hook to manipulate user-defined data in-case of assumption success.
    lineno: Line in the code from where asumption succeeded.
    entry: The assumption success message generated from assume() call
    """
    pass

