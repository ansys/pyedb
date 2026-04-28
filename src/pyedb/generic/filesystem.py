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

import os
import pathlib
import secrets
import shutil
import string
from types import TracebackType

from pyedb.generic.settings import settings
from pyedb.misc.decorators import deprecated, deprecated_class


@deprecated("Please use pathlib.Path.glob for file searching.")
def search_files(dirname: str, pattern: str = "*") -> list[str]:
    """Search for files inside a directory given a specific pattern.

    Parameters
    ----------
    dirname : str
        Directory where the search will be performed.
    pattern : str, optional
        Pattern to match files against. The default is ``"*"``, which matches all files.

    Returns
    -------
    list

    """
    return [os.path.abspath(i) for i in pathlib.Path(dirname).glob(pattern)]


@deprecated("Please use pathlib.Path(__file__).parent.resolve() for current file location.")
def my_location():
    """Get the normalized path of the current file's directory."""
    return os.path.normpath(os.path.dirname(__file__))


@deprecated_class("This class should only be used for testing purposes.")
class Scratch:
    """Class for managing a scratch directory."""

    def __init__(self, local_path, permission=0o777, volatile=False):
        self._volatile = volatile
        self._cleaned = True
        char_set = string.ascii_uppercase + string.digits
        generator = secrets.SystemRandom()
        self._scratch_path = os.path.normpath(
            os.path.join(local_path, "scratch" + "".join(secrets.SystemRandom.sample(generator, char_set, 6)))
        )
        if os.path.exists(self._scratch_path):
            try:
                self.remove()
            except:
                self._cleaned = False
        if self._cleaned:
            try:
                os.mkdir(self.path)
                os.chmod(self.path, permission)
            except FileNotFoundError as fnf_error:  # Raise error if folder doesn't exist.
                print(fnf_error)

    def __enter__(self) -> "Scratch":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if exc_type or self._volatile:
            self.remove()

    @property
    def path(self) -> str:
        """Get the path of the scratch directory."""
        return self._scratch_path

    @property
    def is_empty(self) -> bool:
        """Check if the scratch directory is empty."""
        return self._cleaned

    def remove(self) -> None:
        """Remove the scratch directory and its contents."""
        try:
            shutil.rmtree(self._scratch_path, ignore_errors=True)
            self._cleaned = True
        except Exception:
            settings.logger.error(f"An error occurred while removing {self._scratch_path}")

    def copyfile(self, src_file: str, dst_filename: str | None = None) -> str:
        """Copy a file to the scratch directory.

        Parameters
        ----------
        src_file : str
            Source file with fullpath.
        dst_filename : str, optional
            Destination filename with the extension. The default is ``None``,
            in which case the destination file is given the same name as the
            source file.

        Returns
        -------
        dst_file : str
            Full path and file name of the copied file.

        """
        if dst_filename:
            dst_file = os.path.join(self.path, dst_filename)
        else:
            dst_file = os.path.join(self.path, os.path.basename(src_file))
        if os.path.exists(dst_file):
            try:
                os.unlink(dst_file)
            except OSError:  # pragma: no cover
                pass
        try:
            shutil.copy2(src_file, dst_file)
        except FileNotFoundError as fnf_error:
            print(fnf_error)

        return dst_file

    def copyfolder(self, src_folder: str, destfolder: str | None = None) -> str:
        """Copy a folder to the scratch directory.

        Parameters
        ----------
        src_folder : str
            Source folder with fullpath.
        destfolder : str, optional
            Destination folder. The default is ``None``, in which case the destination folder
            is given the same name as the source folder.

        Returns
        -------
        destfolder : str
            Full path of the copied folder.

        """
        if not destfolder:
            destfolder = os.path.join(self.path, os.path.split(src_folder)[-1])
        shutil.copytree(src_folder, destfolder, dirs_exist_ok=True)
        return destfolder


@deprecated("Please use pathlib.Path.glob for file searching.")
def get_json_files(start_folder):
    """Get the absolute path to all JSON files in start_folder.

    Parameters
    ----------
    start_folder : str
        Path to the folder where the JSON files are located.

    Returns
    -------
    list
         List of paths to JSON files in start_folder.

    """
    return [y for x in os.walk(start_folder) for y in search_files(x[0], "*.json")]
