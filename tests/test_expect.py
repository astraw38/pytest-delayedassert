import pytest

pytest_plugins = ("pytester",)


@pytest.fixture(
    params=["pytest.assume({expr}, {msg})", "with pytest.assume: assert {expr}, {msg}"],
)
def assume_call(request):
    return request.param


def test_passing_expect(testdir, assume_call):
    testdir.makepyfile(
        """
        import pytest

        def test_func():
            {}
        """.format(
            assume_call.format(expr="1==1", msg=None)
        )
    )
    result = testdir.runpytest_inprocess()
    result.assert_outcomes(1, 0, 0)
    assert "1 passed" in result.stdout.str()


def test_failing_expect(testdir, assume_call):
    testdir.makepyfile(
        """
        import pytest
        def test_func():
            {}
        """.format(
            assume_call.format(expr="1==2", msg=None)
        )
    )
    result = testdir.runpytest_inprocess()
    result.assert_outcomes(0, 0, 1)
    assert "1 failed" in result.stdout.str()
    assert "1 Failed Assumptions" in result.stdout.str()
    assert "pytest_pyfunc_call" not in result.stdout.str()


def test_multi_pass_one_failing_expect(testdir, assume_call):
    testdir.makepyfile(
        """
        import pytest
        def test_func():
            {}
            {}
            {}
            {}
        """.format(
            assume_call.format(expr='"xyz" in "abcdefghijklmnopqrstuvwxyz"', msg=None),
            assume_call.format(expr="2==2", msg=None),
            assume_call.format(expr="1==2", msg=None),
            assume_call.format(expr='"xyz" in "abcd"', msg=None),
        )
    )
    result = testdir.runpytest_inprocess()
    result.assert_outcomes(0, 0, 1)
    assert "1 failed" in result.stdout.str()
    assert "2 Failed Assumptions" in result.stdout.str()
    assert "pytest_pyfunc_call" not in result.stdout.str()


def test_passing_expect_doesnt_cloak_assert(testdir, assume_call):
    testdir.makepyfile(
        """
        import pytest
        def test_func():
            {}
            assert 1 == 2
        """.format(
            assume_call.format(expr="1==1", msg=None)
        )
    )
    result = testdir.runpytest_inprocess()
    result.assert_outcomes(0, 0, 1)
    assert "1 failed" in result.stdout.str()
    assert "AssertionError" in result.stdout.str()
    assert "pytest_pyfunc_call" not in result.stdout.str()


def test_failing_expect_doesnt_cloak_assert(testdir, assume_call):
    testdir.makepyfile(
        """
        import pytest
        def test_func():
            {}
            assert 1 == 2
        """.format(
            assume_call.format(expr="1==2", msg=None)
        )
    )
    result = testdir.runpytest_inprocess()
    result.assert_outcomes(0, 0, 1)
    assert "1 failed" in result.stdout.str()
    assert "AssertionError" in result.stdout.str()
    assert "1 Failed Assumptions" in result.stdout.str()
    assert "pytest_pyfunc_call" not in result.stdout.str()


def test_failing_expect_doesnt_cloak_assert_withrepr(testdir, assume_call):
    testdir.makepyfile(
        """
        import pytest
        def test_func():
            a = 1
            b = 2
            {}
            assert a == b
        """.format(
            assume_call.format(expr="a==b", msg=None)
        )
    )
    result = testdir.runpytest_inprocess()
    result.assert_outcomes(0, 0, 1)
    assert "1 failed" in result.stdout.str()
    assert "AssertionError" in result.stdout.str()
    assert "1 Failed Assumptions:" in result.stdout.str()
    assert "pytest_pyfunc_call" not in result.stdout.str()


def test_msg_is_in_output(testdir, assume_call):
    testdir.makepyfile(
        """
        import pytest
        def test_func():
            a = 1
            b = 2
            {}
        """.format(
            assume_call.format(expr="a==b", msg='"a:%s b:%s" % (a,b)')
        )
    )
    result = testdir.runpytest_inprocess()
    result.assert_outcomes(0, 0, 1)
    assert "1 failed" in result.stdout.str()
    assert "1 Failed Assumptions" in result.stdout.str()
    assert "a:1 b:2" in result.stdout.str()
    assert "pytest_pyfunc_call" not in result.stdout.str()


def test_with_locals(testdir, assume_call):
    testdir.makepyfile(
        """
        import pytest
        def test_func():
            a = 1
            b = 2
            {}
        """.format(
            assume_call.format(expr="a==b", msg=None)
        )
    )
    result = testdir.runpytest_inprocess("--showlocals")
    result.assert_outcomes(0, 0, 1)
    stdout = result.stdout.str()
    assert "1 failed" in stdout
    assert "1 Failed Assumptions" in stdout
    assert "a          = 1" in stdout
    assert "b          = 2" in stdout
    assert "pytest_pyfunc_call" not in result.stdout.str()


def test_without_locals(testdir, assume_call):
    testdir.makepyfile(
        """
        import pytest
        def test_func():
            a = 1
            b = 2
            {}
        """.format(
            assume_call.format(expr="a==b", msg=None)
        )
    )
    result = testdir.runpytest_inprocess()
    stdout = result.stdout.str()
    result.assert_outcomes(0, 0, 1)
    assert "1 failed" in stdout
    assert "1 Failed Assumptions" in stdout
    assert "a          = 1" not in stdout
    assert "b          = 2" not in stdout


def test_xfail_assumption(testdir, assume_call):
    testdir.makepyfile(
        """
        import pytest
        @pytest.mark.xfail(run=True, reason="testfail")
        def test_func():
            {}
        """.format(
            assume_call.format(expr="1==2", msg=None)
        )
    )
    result = testdir.runpytest_inprocess("-rxs")
    stdout = result.stdout.str()
    outcomes = result.parseoutcomes()
    assert outcomes.get("xfailed", 0) == 1
    assert "testfail" in stdout

def test_xfail_strict_assumption(testdir, assume_call):
    testdir.makepyfile(
        """
        import pytest
        @pytest.mark.xfail(run=True, reason="testfail", strict=True)
        def test_func():
            {}
        """.format(
            assume_call.format(expr="1==2", msg=None)
        )
    )
    result = testdir.runpytest_inprocess("-rxs")
    stdout = result.stdout.str()
    outcomes = result.parseoutcomes()
    assert outcomes.get("xfailed", 0) == 1
    assert "testfail" in stdout


def test_xpass_assumption(testdir, assume_call):
    testdir.makepyfile(
        """
        import pytest
        @pytest.mark.xfail(run=True, reason="testfail")
        def test_func():
            {}
        """.format(
            assume_call.format(expr=True, msg=None)
        )
    )
    result = testdir.runpytest_inprocess()
    outcomes = result.parseoutcomes()
    assert outcomes.get("xpassed", 0) == 1


def test_xpass_strict_assumption(testdir, assume_call):
    testdir.makepyfile(
        """
        import pytest
        @pytest.mark.xfail(run=True, reason="testfail", strict=True)
        def test_func():
            {}
        """.format(
            assume_call.format(expr="2==2", msg=None)
        )
    )
    result = testdir.runpytest_inprocess("-rxs")
    stdout = result.stdout.str()
    outcomes = result.parseoutcomes()
    assert outcomes.get("failed", 0) == 1
    assert "[XPASS(strict)]" in stdout


def test_bytecode(testdir, assume_call):
    testdir.makepyfile(
        """
        import pytest

        def test_func():
            {}
        """.format(
            assume_call.format(expr='b"\x01" == b"\x5b"', msg=None)
        ).encode()
    )
    result = testdir.runpytest_inprocess()
    result.assert_outcomes(0, 0, 1)
    assert "1 failed" in result.stdout.str()


def test_unicode(testdir, assume_call):
    testdir.makepyfile(
        """
        import pytest

        def test_func():
            {}
        """.format(
            assume_call.format(expr='u"\x5b" == u"\x5a"', msg=None)
        )
    )
    result = testdir.runpytest_inprocess()
    result.assert_outcomes(0, 0, 1)
    assert "1 failed" in result.stdout.str()


def test_mixed_stringtypes(testdir, assume_call):
    testdir.makepyfile(
        """
        import pytest

        def test_func():
            {}
        """.format(
            assume_call.format(expr='b"\x5b" == u"\x5a"', msg=None)
        )
    )
    result = testdir.runpytest_inprocess()
    result.assert_outcomes(0, 0, 1)
    assert "1 failed" in result.stdout.str()


def test_with_tb(testdir, assume_call):
    testdir.makepyfile(
        """
        import pytest
        
        def failing_func():
            assert False

        def test_func():
            {}
            failing_func()
        """.format(
            assume_call.format(expr="1==2", msg=None)
        )
    )
    result = testdir.runpytest_inprocess()
    result.assert_outcomes(0, 0, 1)
    assert "1 failed" in result.stdout.str()
    tb = """
    def failing_func():
>       assert False
"""
    assert tb in result.stdout.str()


def test_assume_pass_hook(testdir):
    """
    Make sure that pytest_assume_pass works.
    Also assure proper return value from pytest.assume().
    """

    # create a temporary conftest.py file
    testdir.makeconftest(
        """
        import pytest

        def pytest_assume_pass(lineno, entry):
            print ("Inside assume_pass hook")
            print ("lineno = %s, entry = %s" % (lineno, entry))
    """
    )

    # create a temporary pytest test file
    testdir.makepyfile(
        """
        import pytest

        def failing_call():
            assert False

        def test_pass():
            ret = pytest.assume(1==1)
            print ("Retval for pass assume = %s" % ret)
            failing_call()
    """
    )

    # run all tests with pytest
    result = testdir.runpytest_inprocess()

    # assert_outcomes = (passed, skipped, failed)
    result.assert_outcomes(0, 0, 1)

    assert "Inside assume_pass hook" in result.stdout.str()
    assert "lineno = " in result.stdout.str()
    assert "Retval for pass assume = True" in result.stdout.str()


def test_assume_fail_hook(testdir):
    """
    Make sure that pytest_assume_fail works.
    Also assure proper return value from pytest.assume().
    """

    # create a temporary conftest.py file
    testdir.makeconftest(
        """
        import pytest

        def pytest_assume_fail(lineno, entry):
            print ("Inside assume_fail hook")
            print ("lineno = %s, entry = %s" % (lineno, entry))
    """
    )

    # create a temporary pytest test file
    testdir.makepyfile(
        """
        import pytest

        def test_fail():
            ret = pytest.assume(1==2)
            print ("Retval for fail assume = %s" % ret)
    """
    )

    # run all tests with pytest
    result = testdir.runpytest_inprocess()
    result.assert_outcomes(0, 0, 1)
    assert "Inside assume_fail hook" in result.stdout.str()
    assert "lineno = " in result.stdout.str()
    assert "Retval for fail assume = False" in result.stdout.str()


def test_doesnt_catch_generic_exceptions(testdir):
    """Let exceptions not related to AssertionErrors to fail the test"""

    testdir.makepyfile(
        """
        import pytest
        
        def test_generic_exception():
            with pytest.assume:
                raise ValueError()
    """
    )

    # run all tests with pytest
    result = testdir.runpytest_inprocess()
    result.assert_outcomes(0, 0, 1)
    assert "test_doesnt_catch_generic_exceptions.py:5: ValueError" in result.stdout.str()


def test_catches_subclass_of_assertionerror(testdir):
    """Catch for assumption AssertionErrors and subclasses"""

    testdir.makepyfile(
        """
        import pytest
        
        class DummyAssertionError(AssertionError):
            pass

        def test_assertionerror_subclass():
            with pytest.assume:
                raise DummyAssertionError()
        """
    )

    # run all tests with pytest
    result = testdir.runpytest_inprocess()
    result.assert_outcomes(0, 0, 1)
    assert "test_catches_subclass_of_assertionerror.py:8: FailedAssumption" in result.stdout.str()


# def test_flaky(testdir):
#     testdir.makepyfile(
#         """
#         import pytest
#
#         @pytest.mark.flaky(reruns=2)
#         def test_func():
#             pytest.assume(False)
#         """)
#     result = testdir.runpytest_inprocess("-p", "no:flaky")
#     result.assert_outcomes(0, 0, 1)
#     assert '1 failed' in result.stdout.str()
#     assert "2 rerun" in result.stdout.str()
#
# def test_flaky2(testdir):
#     testdir.makepyfile(
#         """
#         import pytest
#         from flaky import flaky
#
#         @flaky
#         def test_func():
#             pytest.assume(False)
#         """)
#     result = testdir.runpytest_inprocess()
#     result.assert_outcomes(0, 0, 1)
#     assert '1 failed' in result.stdout.str()


def test_summary_report_hook_with_new_hook(testdir):
    """
    Make sure that pytest_assume_summary_report works.
    """

    # create a temporary conftest.py file
    testdir.makeconftest(
        """
        import pytest
        
        def pytest_assume_summary_report(failed_assumptions):
            print ("Inside summary_report hook")
        
            required_list = []
            for x in failed_assumptions:
                if getattr(pytest, "_showlocals"):
                    ele = x.longrepr()
                else:
                    ele = x.repr()

                msg = "AssumptionFailure: " + ele.split('AssertionError:')[1].split('assert')[0].strip()
                if ", line = " not in msg:
                    line_num = ele.split('AssumptionFailure')[0].split(':')[-2]
                    required_list.append(msg + ', line = ' + line_num)
                else:
                    required_list.append(msg)
            content = '\\n'.join(x for x in required_list)
            return content
        """
    )

    # create a temporary pytest test file
    testdir.makepyfile(
        """
        import pytest
        import logging
        
        logging.basicConfig(level=logging.DEBUG)
        
        def test_1():
            pytest.assume(1==2, "1st failure")
            pytest.assume(2==3, "2nd failure")
            pytest.assume(3==4, "3rd failure")
            pytest.assume(4==5, "4th failure")
        """
    )

    # run all tests with pytest
    result = testdir.runpytest_inprocess()
    result.assert_outcomes(0, 0, 1)
    assert "Inside summary_report hook" in result.stdout.str()
    assert "AssumptionFailure: 1st failure, line = 7" in result.stdout.str()
    assert "AssumptionFailure: 2nd failure, line = 8" in result.stdout.str()
    assert "AssumptionFailure: 3rd failure, line = 9" in result.stdout.str()
    assert "AssumptionFailure: 4th failure, line = 10" in result.stdout.str()


def test_summary_report_hook_with_legacy_implementation(testdir):
    """
    Make sure that summary report gets printed in older format.
    """
    # create a temporary pytest test file
    testdir.makepyfile(
        """
        import pytest
        import logging
        
        logging.basicConfig(level=logging.DEBUG)
        
        def test_1():
            pytest.assume(1==2, "1st failure")
            pytest.assume(2==3, "2nd failure")
            pytest.assume(3==4, "3rd failure")
            pytest.assume(4==5, "4th failure")
        """
    )

    # run all tests with pytest
    result = testdir.runpytest_inprocess()
    result.assert_outcomes(0, 0, 1)
    assert "AssertionError: 1st failure" in result.stdout.str()
    assert "AssertionError: 2nd failure" in result.stdout.str()
    assert "AssertionError: 3rd failure" in result.stdout.str()
    assert "AssertionError: 4th failure" in result.stdout.str()


def test_unittest_based_tests(testdir):
    """
    Unittest-based tests do not use the 'pytest_pyfunc_call' hook; so we can swallow exceptions if using
    the context-based assumption.
    """
    testdir.makepyfile(
        """
        import pytest
        
        from unittest import TestCase
        
        def test_bar():
            with pytest.assume:
                assert 1==2
        
        class Foo(TestCase):
            def test_foo(self):
                with pytest.assume:
                    assert 1==2
        
            def test_bar(self):
                assert 1==2
    """
    )
    result = testdir.runpytest_inprocess()
    result.assert_outcomes(0, 0, 3)


def test_report_sections(testdir):
    testdir.makepyfile(
        """
        import pytest
        import logging
        from pytest import assume
        logging.getLogger().setLevel(logging.DEBUG)

        @pytest.fixture
        def setup_teardown():
            logging.info("Setup")
            yield
            logging.info("Teardown")

        def test_fail_assume(setup_teardown):
            logging.info("This is a test log")
            with assume: assert 1 == 2
        """
    )
    result = testdir.runpytest_inprocess()
    result.assert_outcomes(failed=1)
    assert "Captured log call" in "\n".join(result.outlines)
