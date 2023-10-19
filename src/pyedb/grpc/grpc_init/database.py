"""Database."""
import os
import sys
import ansys.edb

from pyedb import __version__
from pyedb.edb_logger import pyedb_logger
from pyedb.generic.general_methods import settings
from ansys.edb.session import launch_session
from pyedb.misc.misc import list_installed_ansysem


class EdbGrpc(object):
    """Edb Dot Net Class."""

    def __init__(self, edbversion, port):
        self._global_logger = pyedb_logger
        self.logger = pyedb_logger
        if not edbversion:  # pragma: no cover
            try:
                edbversion = "20{}.{}".format(list_installed_ansysem()[0][-3:-1], list_installed_ansysem()[0][-1:])
                self.logger.info("Edb version " + edbversion)
            except IndexError:
                raise Exception("No ANSYSEM_ROOTxxx is found.")
        self.edbversion = edbversion
        self.logger.info("Logger is initialized in EDB.")
        self.logger.info("legacy v%s", __version__)
        self.logger.info("Python version %s", sys.version)

        self.base_path = settings.pyedb_server_path
        sys.path.append(self.base_path)
        os.environ["ECAD_TRANSLATORS_INSTALL_DIR"] = self.base_path
        oaDirectory = os.path.join(self.base_path, "common", "oa")
        os.environ["ANSYS_OADIR"] = oaDirectory
        os.environ["PATH"] = "{};{}".format(os.environ["PATH"], self.base_path)
        "Starting grpc server"
        session = launch_session(self.base_path, port)
        if session:
            self.logger("Grpc session started")
        self._edb = ansys.edb