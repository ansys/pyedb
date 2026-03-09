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

from pathlib import Path
import shutil
import tempfile
import warnings
import zipfile

from pyedb.edb_logger import EdbLogger
from pyedb.generic.general_methods import settings

# Initialize logger
pyedb_logger = EdbLogger(settings=settings)

from ansys.tools.common.example_download import download_manager

EXAMPLES_PATH = Path(tempfile.gettempdir()) / "PyAEDTExamples"


def delete_downloads() -> None:
    """Delete all downloaded examples to free space or update the files.

    Examples
    --------
    >>> import pyedb.misc.downloads as downloads
    >>> downloads.delete_downloads()

    """
    shutil.rmtree(EXAMPLES_PATH, ignore_errors=True)


def list_examples_files(folder) -> list:
    """List all files in a folder of the example-data repository.

    Parameters
    ----------
    folder : str
        The folder in the GitHub repository to list files from, e.g., "pyaedt/sbr/".

    Returns
    -------
    list
        A list of file paths in the specified folder.
    """
    import requests

    # Adding a trailing slash to ensure we only match files in the specified folder
    # Otherwise an input of "project/folder" would also match "project/folder_diff"
    folder_prefix = folder if folder.endswith("/") else folder + "/"
    url = "https://api.github.com/repos/ansys/example-data/git/trees/main?recursive=1"
    headers = {"Accept": "application/vnd.github.v3+json"}
    response = requests.get(url, headers=headers)  # nosec B113 : this is a trusted URL
    response.raise_for_status()
    tree = response.json()["tree"]

    files = []
    for item in tree:
        if item["type"] == "blob" and item["path"].startswith(folder_prefix):
            files.append(item["path"])
    return files


def _download_file(
    directory: str,
    filename: str,
    destination: str,
    strip_prefix: str | Path | None = None,
    force: bool = False,
) -> str:
    """Download a file from the example repository.

    Parameters
    ----------
    directory : str
        Directory path in the repository.
    filename : str
        File name to download.
    destination : str
        Destination path for the download.
    strip_prefix : str | Path, optional
        A prefix to strip from the relative path when saving the file locally.
        The default is ``None``.
    force : bool, optional
        Force to delete cache and download files again.
        The default is ``False``.

    Returns
    -------
    str
        Path to the downloaded file.

    """
    local_relative_path = Path(directory) / filename
    if strip_prefix:
        local_relative_path = local_relative_path.relative_to(strip_prefix)

    if not destination:
        destination = EXAMPLES_PATH / local_relative_path
    else:
        destination = Path(destination) / local_relative_path

    try:
        if not destination.exists() or force:
            pyedb_logger.debug(f"Downloading file from {Path(Path(directory) / filename).as_posix()} to {destination}")
            file_path = download_manager.download_file(
                filename=filename,
                directory=directory,
                destination=str(destination.parent),
                force=force,
            )
        else:
            file_path = str(destination)
            pyedb_logger.debug(f"File already exists in {destination}. Skipping download.")
    except Exception as e:
        raise RuntimeError(f"Failed to download file from {Path(directory) / filename}.") from e

    if settings.remote_rpc_session:
        remote_path = Path(settings.remote_rpc_session_temp_folder) / Path(file_path)
        if not settings.remote_rpc_session.filemanager.pathexists(settings.remote_rpc_session_temp_folder):
            settings.remote_rpc_session.filemanager.makedirs(settings.remote_rpc_session_temp_folder)
        settings.remote_rpc_session.filemanager.upload(file_path, str(remote_path))
        file_path = remote_path

    return file_path


def _download_folder(
    directory: str, destination: str, strip_prefix: str | Path | None = None, force: bool = False
) -> str:
    """Download a file from the example repository.

    Parameters
    ----------
    directory : str
        Directory path in the repository.
    filename : str
        File name to download.
    destination : str
        Destination path for the download.
    strip_prefix : str | Path | None, optional
        A prefix to strip from the relative path when saving the file locally.
        The default is ``None``.
    force : bool, optional
        Force to delete cache and download files again.
        The default is ``False``.

    Returns
    -------
    str
        Path to the downloaded folder.

    """
    files = list_examples_files(directory)
    for file in files:
        directory, filename = Path(file).parent.as_posix(), Path(file).name
        _download_file(directory, filename, destination=destination, strip_prefix=strip_prefix, force=force)

    return str(Path(destination) / directory)


###############################################################################


def download_aedb(destination: str | None = None) -> str:
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
    warnings.warn("This design has been removed, consider using another one.")


def download_edb_merge_utility(force_download: bool = False, destination: str | None = None) -> str:
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
    'C:/Users/user/AppData/local/temp/PyAEDTExamples/wpf_edb_merge/merge_wizard.py'

    """
    if not destination:  # pragma: no cover
        destination = EXAMPLES_PATH

    _download_file(
        "pyaedt/wpf_edb_merge/board.aedb", "edb.def", destination, strip_prefix="pyaedt", force=force_download
    )
    _download_file(
        "pyaedt/wpf_edb_merge/package.aedb", "edb.def", destination, strip_prefix="pyaedt", force=force_download
    )
    _download_file(
        "pyaedt/wpf_edb_merge", "merge_wizard_settings.json", destination, strip_prefix="pyaedt", force=force_download
    )

    return _download_file(
        "pyaedt/wpf_edb_merge", "merge_wizard.py", destination, strip_prefix="pyaedt", force=force_download
    )


def download_via_wizard(destination: str | None = None) -> str:
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
    'C:/Users/user/AppData/local/temp/PyAEDTExamples/viawizard_vacuum_FR4.aedt'
    """
    if not destination:  # pragma: no cover
        destination = EXAMPLES_PATH

    return _download_file(
        "pyaedt/via_wizard", "viawizard_vacuum_FR4.aedt", destination, strip_prefix="pyaedt/via_wizard"
    )


def download_touchstone(destination: str | None = None) -> str:
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
    'C:/Users/user/AppData/local/temp/PyAEDTExamples/SSN_ssn.s6p'

    """
    if not destination:  # pragma: no cover
        destination = EXAMPLES_PATH

    return _download_file("pyaedt/touchstone", "SSN_ssn.s6p", destination, strip_prefix="pyaedt/touchstone")


def download_file(directory: str, filename: str | None = None, destination: str | None = None) -> str:
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
    >>> path = pyedb.misc.downloads.download_file("pyaedt/edb/ansys_interposer", "dummy_interposer_hbm.map")
    >>> path
    'C:/Users/user/AppData/local/temp/PyAEDTExamples/pyaedt/edb/ansys_interposer/dummy_interposer_hbm.map'

    """
    if not destination:
        destination = EXAMPLES_PATH

    if filename:
        return _download_file(directory, filename, destination)

    return _download_folder(directory, destination)


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
