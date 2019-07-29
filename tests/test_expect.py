import pytest


pytest_plugins = ("pytester",)


@pytest.mark.parametrize("assume", ["pytest.assume({expr}, {msg})", "with pytest.assume: assert {expr}, {msg}"])
def test_passing_expect(testdir, assume):
    testdir.makepyfile(
        f"""
        import pytest

        def test_func():
            {assume.format(
                expr="1==1",
                msg=None
            )}
        """
    )
    result = testdir.runpytest_inprocess()
    result.assert_outcomes(1, 0, 0)
    assert "1 passed" in result.stdout.str()


@pytest.mark.parametrize("assume", ["pytest.assume({expr}, {msg})", "with pytest.assume: assert {expr}, {msg}"])
def test_failing_expect(testdir, assume):
    testdir.makepyfile(
        f"""
        import pytest
        def test_func():
            {assume.format(
                expr="1==2",
                msg=None
            )}
        """
    )
    result = testdir.runpytest_inprocess()
    result.assert_outcomes(0, 0, 1)
    assert "1 failed" in result.stdout.str()
    assert "1 Failed Assumptions" in result.stdout.str()
    assert "pytest_pyfunc_call" not in result.stdout.str()


@pytest.mark.parametrize("assume", ["pytest.assume({expr}, {msg})", "with pytest.assume: assert {expr}, {msg}"])
def test_multi_pass_one_failing_expect(testdir, assume):
    testdir.makepyfile(
        f"""
        import pytest
        def test_func():
            {assume.format(
                expr='"xyz" in "abcdefghijklmnopqrstuvwxyz"',
                msg=None
            )}
            {assume.format(
                expr="2==2",
                msg=None,
            )}
            {assume.format(
                expr="1==2",
                msg=None,
            )}
            {assume.format(
                expr='"xyz" in "abcd"',
                msg=None,
            )}
        """
    )
    result = testdir.runpytest_inprocess()
    result.assert_outcomes(0, 0, 1)
    assert "1 failed" in result.stdout.str()
    assert "2 Failed Assumptions" in result.stdout.str()
    assert "pytest_pyfunc_call" not in result.stdout.str()


@pytest.mark.parametrize("assume", ["pytest.assume({expr}, {msg})", "with pytest.assume: assert {expr}, {msg}"])
def test_passing_expect_doesnt_cloak_assert(testdir, assume):
    testdir.makepyfile(
        f"""
        import pytest
        def test_func():
            {assume.format(
                expr='1==1',
                msg=None
            )}
            assert 1 == 2
        """
    )
    result = testdir.runpytest_inprocess()
    result.assert_outcomes(0, 0, 1)
    assert "1 failed" in result.stdout.str()
    assert "AssertionError" in result.stdout.str()
    assert "pytest_pyfunc_call" not in result.stdout.str()


@pytest.mark.parametrize("assume", ["pytest.assume({expr}, {msg})", "with pytest.assume: assert {expr}, {msg}"])
def test_failing_expect_doesnt_cloak_assert(testdir, assume):
    testdir.makepyfile(
        f"""
        import pytest
        def test_func():
            {assume.format(
                expr='1==2',
                msg=None
            )}
            assert 1 == 2
        """
    )
    result = testdir.runpytest_inprocess()
    result.assert_outcomes(0, 0, 1)
    assert "1 failed" in result.stdout.str()
    assert "AssertionError" in result.stdout.str()
    assert "1 Failed Assumptions" in result.stdout.str()
    assert "pytest_pyfunc_call" not in result.stdout.str()


@pytest.mark.parametrize("assume", ["pytest.assume({expr}, {msg})", "with pytest.assume: assert {expr}, {msg}"])
def test_failing_expect_doesnt_cloak_assert_withrepr(testdir, assume):
    testdir.makepyfile(
        f"""
        import pytest
        def test_func():
            a = 1
            b = 2
            {assume.format(
                expr='a==b',
                msg=None
            )}
            assert a == b
        """
    )
    result = testdir.runpytest_inprocess()
    result.assert_outcomes(0, 0, 1)
    assert "1 failed" in result.stdout.str()
    assert "AssertionError" in result.stdout.str()
    assert "1 Failed Assumptions:" in result.stdout.str()
    assert "pytest_pyfunc_call" not in result.stdout.str()


@pytest.mark.parametrize("assume", ["pytest.assume({expr}, {msg})", "with pytest.assume: assert {expr}, {msg}"])
def test_msg_is_in_output(testdir, assume):
    testdir.makepyfile(
        f"""
        import pytest
        def test_func():
            a = 1
            b = 2
            {assume.format(
                expr='a==b',
                msg='"a:%s b:%s" % (a,b)'
            )}
        """
    )
    result = testdir.runpytest_inprocess()
    result.assert_outcomes(0, 0, 1)
    assert "1 failed" in result.stdout.str()
    assert "1 Failed Assumptions" in result.stdout.str()
    assert "a:1 b:2" in result.stdout.str()
    assert "pytest_pyfunc_call" not in result.stdout.str()


@pytest.mark.parametrize("assume", ["pytest.assume({expr}, {msg})", "with pytest.assume: assert {expr}, {msg}"])
def test_with_locals(testdir, assume):
    testdir.makepyfile(
        f"""
        import pytest
        def test_func():
            a = 1
            b = 2
            {assume.format(
                expr='a==b',
                msg=None
            )}
        """
    )
    result = testdir.runpytest_inprocess("--showlocals")
    result.assert_outcomes(0, 0, 1)
    stdout = result.stdout.str()
    assert "1 failed" in stdout
    assert "1 Failed Assumptions" in stdout
    assert "a          = 1" in stdout
    assert "b          = 2" in stdout
    assert "pytest_pyfunc_call" not in result.stdout.str()


@pytest.mark.parametrize("assume", ["pytest.assume({expr}, {msg})", "with pytest.assume: assert {expr}, {msg}"])
def test_without_locals(testdir, assume):
    testdir.makepyfile(
        f"""
        import pytest
        def test_func():
            a = 1
            b = 2
            {assume.format(
                expr='a==b',
                msg=None
            )}
        """
    )
    result = testdir.runpytest_inprocess()
    stdout = result.stdout.str()
    result.assert_outcomes(0, 0, 1)
    assert "1 failed" in stdout
    assert "1 Failed Assumptions" in stdout
    assert "a          = 1" not in stdout
    assert "b          = 2" not in stdout


@pytest.mark.parametrize("assume", ["pytest.assume({expr}, {msg})", "with pytest.assume: assert {expr}, {msg}"])
def test_xfail_assumption(testdir, assume):
    testdir.makepyfile(
        f"""
        import pytest
        @pytest.mark.xfail(run=True, reason="testfail")
        def test_func():
            {assume.format(
                expr='1==2',
                msg=None
            )}
        """
    )
    result = testdir.runpytest_inprocess("-rxs")
    stdout = result.stdout.str()
    outcomes = result.parseoutcomes()
    assert outcomes.get("xfailed", 0) == 1
    assert "testfail" in stdout


@pytest.mark.parametrize("assume", ["pytest.assume({expr}, {msg})", "with pytest.assume: assert {expr}, {msg}"])
def test_xpass_assumption(testdir, assume):
    testdir.makepyfile(
        f"""
        import pytest
        @pytest.mark.xfail(run=True, reason="testfail")
        def test_func():
            {assume.format(
                expr=True,
                msg=None
            )}
        """
    )
    result = testdir.runpytest_inprocess()
    outcomes = result.parseoutcomes()
    assert outcomes.get("xpassed", 0) == 1


@pytest.mark.parametrize("assume", ["pytest.assume({expr}, {msg})", "with pytest.assume: assert {expr}, {msg}"])
def test_bytecode(testdir, assume):
    testdir.makepyfile(
        b"""
        import pytest

        def test_func():
            pytest.assume(b"\x01" == b"\x5b")
        """
    )
    result = testdir.runpytest_inprocess()
    result.assert_outcomes(0, 0, 1)
    assert "1 failed" in result.stdout.str()


@pytest.mark.parametrize("assume", ["pytest.assume({expr}, {msg})", "with pytest.assume: assert {expr}, {msg}"])
def test_unicode(testdir, assume):
    testdir.makepyfile(
        """
        import pytest

        def test_func():
            pytest.assume(u"\x5b" == u"\x5a")
        """
    )
    result = testdir.runpytest_inprocess()
    result.assert_outcomes(0, 0, 1)
    assert "1 failed" in result.stdout.str()


@pytest.mark.parametrize("assume", ["pytest.assume({expr}, {msg})", "with pytest.assume: assert {expr}, {msg}"])
def test_mixed_stringtypes(testdir, assume):
    testdir.makepyfile(
        """
        import pytest

        def test_func():
            pytest.assume(b"\x5b" == u"\x5a")
        """
    )
    result = testdir.runpytest_inprocess()
    result.assert_outcomes(0, 0, 1)
    assert "1 failed" in result.stdout.str()


@pytest.mark.parametrize("assume", ["pytest.assume({expr}, {msg})", "with pytest.assume: assert {expr}, {msg}"])
def test_with_tb(testdir, assume):
    testdir.makepyfile(
        f"""
        import pytest
        
        def failing_func():
            assert False

        def test_func():
            {assume.format(
                expr="1==2",
                msg=None
            )}
            failing_func()
        """
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


#
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
