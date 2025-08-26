import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

DOTNET_ROOT = "dummy/root/path"
DOTNET_ROOT_PATH = Path(DOTNET_ROOT)
DOTNETCORE2_FILE = "dummy/dotnetcore2/file"
DOTNETCORE2_BIN = "dummy/dotnetcore2/bin"
PYEDB_FILE = "dummy/pyedb/file"


@pytest.fixture
def clean_environment():
    initial_sys_modules = sys.modules.copy()
    initial_os_environ = os.environ.copy()

    if "pyedb.dotnet.clr_module" in sys.modules:
        del sys.modules["pyedb.dotnet.clr_module"]
    if "DOTNET_ROOT" in os.environ:
        del os.environ["DOTNET_ROOT"]

    yield

    sys.modules.clear()
    sys.modules.update(initial_sys_modules)
    os.environ.clear()
    os.environ.update(initial_os_environ)


@pytest.mark.skipif(os.name != "posix", reason="test for linux behavior")
@patch("pythonnet.load")
@patch("clr_loader.get_coreclr")
def test_use_system_dotnet(mock_get_coreclr, mock_load, clean_environment):
    mock_runtime = MagicMock()
    mock_runtime.dotnet_root = DOTNET_ROOT_PATH
    mock_get_coreclr.return_value = mock_runtime

    import pyedb.dotnet.clr_module as cm

    assert cm.is_clr
    assert DOTNET_ROOT_PATH.as_posix() == os.environ["DOTNET_ROOT"]
    del os.environ["DOTNET_ROOT"]


@pytest.mark.skipif(os.name != "posix", reason="test for linux behavior")
@patch("dotnetcore2.__file__", new=DOTNETCORE2_FILE)
@patch("pythonnet.load")
@patch("clr_loader.get_coreclr", side_effect=Exception("Dummy exception"))
def test_use_dotnetcore2(mock_get_coreclr, mock_load, clean_environment, capsys):
    import pyedb.dotnet.clr_module as cm

    captured = capsys.readouterr()
    from pyedb.dotnet.clr_module import LINUX_WARNING

    assert cm.is_clr
    assert DOTNETCORE2_BIN == os.environ["DOTNET_ROOT"]
    assert LINUX_WARNING in captured.out


@pytest.mark.skipif(os.name != "posix", reason="test for linux behavior")
@patch("dotnetcore2.__file__", new=DOTNETCORE2_FILE)
@patch("pythonnet.load")
@patch("clr_loader.find_runtimes", return_value=[])
def test_use_dotnet_root_env_variable_failure(mock_find_runtimes, mock_load, clean_environment, capsys):
    os.environ["DOTNET_ROOT"] = DOTNET_ROOT

    with pytest.raises(RuntimeError):
        import pyedb.dotnet.clr_module  # noqa: F401


@pytest.mark.skipif(os.name != "posix", reason="test for linux behavior")
@patch("dotnetcore2.__file__", new=DOTNETCORE2_FILE)
@patch("pythonnet.load")
def test_use_dotnet_root_env_variable_success_dotnetcore2(mock_load, clean_environment, capsys):
    os.environ["DOTNET_ROOT"] = DOTNETCORE2_BIN

    import pyedb.dotnet.clr_module as cm

    captured = capsys.readouterr()
    from pyedb.dotnet.clr_module import LINUX_WARNING

    assert cm.is_clr
    assert DOTNETCORE2_BIN == os.environ["DOTNET_ROOT"]
    assert LINUX_WARNING not in captured.out


@pytest.mark.skipif(os.name != "posix", reason="test for linux behavior")
@patch("dotnetcore2.__file__", new=DOTNETCORE2_FILE)
@patch("pythonnet.load")
@patch("clr_loader.find_runtimes")
def test_use_dotnet_root_env_variable_success(mock_find_runtimes, mock_load, clean_environment, capsys):
    os.environ["DOTNET_ROOT"] = DOTNET_ROOT
    mock_runtime = MagicMock()
    mock_runtime.name = "Microsoft.NETCore.App"
    mock_find_runtimes.return_value = [mock_runtime]

    import pyedb.dotnet.clr_module  # noqa: F401

    assert os.environ["DOTNET_ROOT"]
