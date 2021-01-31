import pytest
import platform
import testspace_colab.client as client


@pytest.mark.parametrize("system_name", ["Linux", "Darwin", "Windows"])
def test_path(system_name, mocker):
    """Verify that the client resolve the path appropriately

    :param system_name: System name to patch
    :param mocker: pytest mocker fixture
    """
    mocker.patch("platform.system", return_value=system_name)
    binary = client.Binary()
    assert platform.system().lower() in str(binary.path)
    assert binary.path.is_file()


def test_unsupported_system(mocker):
    """Check that the ctor raise an exception when binary not found
    :param mocker: pytest mocker fixture
    """
    mocker.patch("platform.system", return_value="Java")
    with pytest.raises(FileNotFoundError) as error:
        client.Binary()
    assert "Could not find testspace binary" in str(error)


def test_version():
    version = client.Binary().version
    assert len(version.split(".")) == 3
    list(map(int, version.split(".")))  # Make sure all elements are integer


@pytest.mark.parametrize("args", [("a", "b", "c"), "a b c"])
def test_exec_with_exceptions(args):
    """ Check that the args are formatted correct and that exceptions are raise"""
    with pytest.raises(ChildProcessError) as error:
        client.Binary().exec(args)
    assert "a b c" in str(error)


def test_exec_no_exception():
    """Checks that not exception are raised"""
    assert client.Binary().exec("--version") == 0
    assert client.Binary().exec("a b c", return_code=None) == 2
    # This should not raise an exception
    client.Binary().exec("a b c", return_code=2)
