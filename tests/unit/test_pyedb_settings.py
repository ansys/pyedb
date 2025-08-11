from unittest.mock import patch

from pyedb.generic.settings import Settings

os_environ = {
    "ANSYSEM_ROOT251": "/fake/path251",
    "ANSYSEM_ROOT252": "/fake/path252",
    "ANSYSEMSV_ROOT251": "/fake/pathSV251",
    "ANSYSEMSV_ROOT252": "/fake/pathSV252",
    "ANSYSEM_PY_CLIENT_ROOT252": "/fake/path_py_client",
}


@patch("os.environ", os_environ)
def test_general():
    settings = Settings()
    settings.specified_version = "2025.1"
    assert settings.INSTALLED_VERSIONS == {
        "2025.2": "/fake/path252",
        "2025.1": "/fake/path251",
    }
    assert settings.INSTALLED_STUDENT_VERSIONS == {
        "2025.2": "/fake/pathSV252",
        "2025.1": "/fake/pathSV251",
    }
    assert settings.INSTALLED_CLIENT_VERSIONS == {"2025.2": "/fake/path_py_client"}
    assert settings.LATEST_VERSION == "2025.2"
    assert settings.LATEST_STUDENT_VERSION == "2025.2"
    assert settings.aedt_installation_path == "/fake/path251"
