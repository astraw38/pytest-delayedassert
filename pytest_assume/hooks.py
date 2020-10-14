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


def pytest_assume_summary_report(failed_assumptions):
    """
    Hook to manipulate the summary that prints at the end.
    User can print the failure summary as per desired format.
    failed_assumptions: List of all failed assume() calls

    return: String representation of the summary report.
    """
    pass
