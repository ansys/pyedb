from pathlib import Path
import tempfile

from pyaedt.downloads import download_file


class Workflow:
    def __init__(self, pedb):
        self._pedb = pedb

    def get_si_verse(self, working_directory: [str, Path] = None):
        """Download SI-verse demo board.

        Parameters
        ----------
        working_directory
        """
        if working_directory is None:
            temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")
            dst = temp_folder.name
        else:
            dst = str(working_directory)
        aedb = download_file(source="edb/ANSYS-HSD_V1.aedb", destination=dst)
        self._pedb.close_edb()
        self._pedb.edbpath = aedb
        self._pedb.open_edb()
