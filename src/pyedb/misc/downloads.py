# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Download example datasets from https://github.com/pyansys/example-data"""

import os
import shutil
import subprocess  # nosec B404
import tempfile
import urllib.request
import zipfile

from pyedb.generic.general_methods import is_linux, settings

tmpfold = tempfile.gettempdir()
EXAMPLE_REPO = "https://github.com/ansys/example-data/raw/main/"
EXAMPLES_PATH = os.path.join(tmpfold, "PyAEDTExamples")


def delete_downloads() -> None:
    """Delete all downloaded examples to free space or update the files.

    Examples
    --------
    >>> import pyedb.misc.downloads as downloads
    >>> downloads.delete_downloads()

    """
    shutil.rmtree(EXAMPLES_PATH, ignore_errors=True)


def _get_file_url(directory: str, filename: str | None = None) -> str:
    """Get the full URL for a file in the example repository.

    Parameters
    ----------
    directory : str
        Directory path in the repository.
    filename : str or None, optional
        File name to append to the URL.
        The default is ``None``.

    Returns
    -------
    str
        Full URL to the file or directory.

    """
    if not filename:
        return EXAMPLE_REPO + "/".join([directory])
    else:
        return EXAMPLE_REPO + "/".join([directory, filename])


def _retrieve_file(
    url: str, filename: str, directory: str, destination: str | None = None, local_paths: list[str] | None = None
) -> None:  # pragma: no cover
    """Download a file from a URL.

    .. warning::
            Do not execute this function with untrusted function argument, environment
            variables or pyedb global settings.
            See the :ref:`security guide<ref_security_consideration>` for details.

    Parameters
    ----------
    url : str
        URL of the file to download.
    filename : str
        Name of the file to download.
    directory : str
        Directory where the file will be saved.
    destination : str or None, optional
        Destination path for the download.
        The default is ``None``.
    local_paths : list[str] or None, optional
        List to append the downloaded file paths.
        The default is ``None``.

    """
    if local_paths is None:
        local_paths = []
    # Check that provided url is pointing to pyaedt-example repo
    if not url.startswith(EXAMPLE_REPO):
        raise ValueError(f"Attempting to download file(s) from url {url} not pointing the to example-data repo.")

    # First check if file has already been downloaded
    if not destination:
        destination = EXAMPLES_PATH
    local_path = os.path.join(destination, directory, os.path.basename(filename))
    local_path_no_zip = local_path.replace(".zip", "")
    if os.path.isfile(local_path_no_zip) or os.path.isdir(local_path_no_zip):
        local_paths.append(local_path_no_zip)

    # grab the correct url retriever
    urlretrieve = urllib.request.urlretrieve
    destination_dir = os.path.join(destination, directory)
    if not os.path.isdir(destination_dir):
        os.makedirs(destination_dir)
    # Perform download
    if is_linux:
        command = ["wget", url, "-O", local_path]
        try:
            subprocess.run(command, check=True)  # nosec
        except subprocess.CalledProcessError as e:  # nosec
            raise RuntimeError("An error occurred while downloading wget") from e
    else:
        _, resp = urlretrieve(url, local_path)
    local_paths.append(local_path)


def _retrieve_folder(
    url: str, directory: str, destination: str | None = None, local_paths: list[str] | None = None
) -> bool:  # pragma: no cover
    """Download a folder from a URL.

    Parameters
    ----------
    url : str
        URL of the folder to download.
    directory : str
        Directory path.
    destination : str or None, optional
        Destination path for the download.
        The default is ``None``.
    local_paths : list[str] or None, optional
        List to append the downloaded file paths.
        The default is ``None``.

    Returns
    -------
    bool
        ``True`` if successful, ``False`` otherwise.

    """
    if local_paths is None:
        local_paths = []
    # First check if folder exists
    import json
    import re

    if not destination:
        destination = EXAMPLES_PATH
    if directory.startswith("pyaedt/"):
        local_path = os.path.join(destination, directory[7:])
    else:
        local_path = os.path.join(destination, directory)

    _get_dir = _get_file_url(directory)
    with urllib.request.urlopen(_get_dir) as response:  # nosec
        data = response.read().decode("utf-8").split("\n")

    if not os.path.isdir(local_path):
        try:
            os.mkdir(local_path)
        except FileNotFoundError:
            os.makedirs(local_path)

    try:
        tree = [i for i in data if '"payload"' in i][0]
        b = re.search(r'>({"payload".+)</script>', tree)
        itemsfromjson = json.loads(b.group(1))
        items = itemsfromjson["payload"]["tree"]["items"]
        for item in items:
            if item["contentType"] == "directory":
                _retrieve_folder(url, item["path"], destination, local_paths)
            else:
                dir_folder = os.path.split(item["path"])
                _download_file(dir_folder[0], dir_folder[1], destination, local_paths)
        return True
    except Exception:
        return False


def _download_file(
    directory: str, filename: str | None = None, destination: str | None = None, local_paths: list[str] | None = None
) -> str:  # pragma: no cover
    """Download a file from the example repository.

    Parameters
    ----------
    directory : str
        Directory path in the repository.
    filename : str or None, optional
        File name to download.
        The default is ``None``.
    destination : str or None, optional
        Destination path for the download.
        The default is ``None``.
    local_paths : list[str] or None, optional
        List to append the downloaded file paths.
        The default is ``None``.

    Returns
    -------
    str
        Path to the downloaded file.

    """
    if local_paths is None:
        local_paths = []
    if not filename:
        if not directory.startswith("pyaedt/"):
            directory = "pyaedt/" + directory
        _retrieve_folder(EXAMPLE_REPO, directory, destination, local_paths)
    else:
        if directory.startswith("pyaedt/"):
            url = _get_file_url(directory, filename)
            directory = directory[7:]
        else:
            url = _get_file_url("pyaedt/" + directory, filename)
        _retrieve_file(url, filename, directory, destination, local_paths)
    if settings.remote_rpc_session:
        remote_path = os.path.join(settings.remote_rpc_session_temp_folder, os.path.split(local_paths[-1])[-1])
        if not settings.remote_rpc_session.filemanager.pathexists(settings.remote_rpc_session_temp_folder):
            settings.remote_rpc_session.filemanager.makedirs(settings.remote_rpc_session_temp_folder)
        settings.remote_rpc_session.filemanager.upload(local_paths[-1], remote_path)
        local_paths[-1] = remote_path
    return local_paths[-1]


###############################################################################
# front-facing functions


def download_aedb(destination: str | None = None) -> str:  # pragma: no cover
    """Download an example of AEDB File and return the def path.

    Examples files are downloaded to a persistent cache to avoid
    re-downloading the same file twice.

    Parameters
    ----------
    destination : str or None, optional
        Path for downloading files.
        The default is ``None``, which uses the user's temp folder.

    Returns
    -------
    str
        Path to the example file.

    Examples
    --------
    Download an example result file and return the path of the file.

    >>> import pyedb.misc.downloads
    >>> path = pyedb.misc.downloads.download_aedb()
    >>> path
    'C:/Users/user/AppData/local/temp/Galileo.aedb'

    """
    local_paths = []
    _download_file("pyaedt/edb/Galileo.aedb", "GRM32ER72A225KA35_25C_0V.sp", destination, local_paths)
    _download_file("pyaedt/edb/Galileo.aedb", "edb.def", destination, local_paths)
    return local_paths[-1]


def download_edb_merge_utility(force_download: bool = False, destination: str | None = None) -> str:  # pragma: no cover
    """Download an example of WPF Project which allows to merge 2 aedb files.

    Examples files are downloaded to a persistent cache to avoid
    re-downloading the same file twice.

    Parameters
    ----------
    force_download : bool, optional
        Force to delete cache and download files again.
        The default is ``False``.
    destination : str or None, optional
        Path for downloading files.
        The default is ``None``, which uses the user's temp folder.

    Returns
    -------
    str
        Path to the example file.

    Examples
    --------
    Download an example result file and return the path of the file.

    >>> import pyedb.misc.downloads
    >>> path = pyedb.misc.downloads.download_edb_merge_utility(force_download=True)
    >>> path
    'C:/Users/user/AppData/local/temp/wpf_edb_merge/merge_wizard.py'

    """
    if not destination:
        destination = EXAMPLES_PATH
    if force_download:
        local_path = os.path.join(destination, "wpf_edb_merge")
        if os.path.exists(local_path):
            shutil.rmtree(local_path, ignore_errors=True)
    local_paths = []
    _download_file("pyaedt/wpf_edb_merge/board.aedb", "edb.def", destination, local_paths)
    _download_file("pyaedt/wpf_edb_merge/package.aedb", "edb.def", destination, local_paths)
    _download_file("pyaedt/wpf_edb_merge", "merge_wizard_settings.json", destination, local_paths)

    _download_file("pyaedt/wpf_edb_merge", "merge_wizard.py", destination, local_paths)
    return local_paths[0]


def download_via_wizard(destination: str | None = None) -> str:  # pragma: no cover
    """Download an example of Hfss Via Wizard and return the def path.

    Examples files are downloaded to a persistent cache to avoid
    re-downloading the same file twice.

    Parameters
    ----------
    destination : str or None, optional
        Path for downloading files.
        The default is ``None``, which uses the user's temp folder.

    Returns
    -------
    str
        Path to the example file.

    Examples
    --------
    Download an example result file and return the path of the file.

    >>> import pyedb.misc.downloads
    >>> path = pyedb.misc.downloads.download_via_wizard()
    >>> path
    'C:/Users/user/AppData/local/temp/pyaedtexamples/Graphic_Card.aedt'

    """

    return _download_file("pyaedt/via_wizard", "viawizard_vacuum_FR4.aedt", destination)


def download_touchstone(destination: str | None = None) -> str:  # pragma: no cover
    """Download an example of touchstone File and return the def path.

    Examples files are downloaded to a persistent cache to avoid
    re-downloading the same file twice.

    Parameters
    ----------
    destination : str or None, optional
        Path for downloading files.
        The default is ``None``, which uses the user's temp folder.

    Returns
    -------
    str
        Path to the example file.

    Examples
    --------
    Download an example result file and return the path of the file.

    >>> import pyedb.misc.downloads
    >>> path = pyedb.misc.downloads.download_touchstone()
    >>> path
    'C:/Users/user/AppData/local/temp/pyaedtexamples/ssn_ssn.s6p'

    """
    local_paths = []
    _download_file("pyaedt/touchstone", "SSN_ssn.s6p", destination, local_paths)
    return local_paths[0]


def download_file(
    directory: str, filename: str | None = None, destination: str | None = None
) -> str:  # pragma: no cover
    """Download file from directory.

    Files are downloaded to a destination. If filename is not specified, the full directory will be downloaded.

    Parameters
    ----------
    directory : str
        Directory name.
    filename : str or None, optional
        File name to download.
        The default is ``None``, which downloads all files inside directory.
    destination : str or None, optional
        Path where files will be downloaded.
        The default is ``None``, which uses the user's temp folder.

    Returns
    -------
    str
        Path to the example file.

    Examples
    --------
    Download an example result file and return the path of the file.

    >>> import pyedb.misc.downloads
    >>> path = pyedb.misc.downloads.download_file("motorcad", "IPM_Vweb_Hairpin.mot")
    >>> path
    'C:/Users/user/AppData/local/temp/PyAEDTExamples/motorcad'

    """
    local_paths = []
    _download_file(directory, filename, destination, local_paths)
    if filename:
        return list(set(local_paths))[0]
    else:
        if not destination:
            destination = EXAMPLES_PATH
        destination_dir = os.path.join(destination, directory)
        return destination_dir


def unzip(source_filename: str, dest_dir: str) -> None:
    """Extract all files from a zip archive.

    Parameters
    ----------
    source_filename : str
        Path to the zip file to extract.
    dest_dir : str
        Destination directory for extracted files.

    Examples
    --------
    >>> import pyedb.misc.downloads as downloads
    >>> downloads.unzip("example.zip", "/path/to/destination")

    """
    with zipfile.ZipFile(source_filename) as zf:
        zf.extractall(dest_dir)
