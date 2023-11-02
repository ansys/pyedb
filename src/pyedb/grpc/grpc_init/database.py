"""Database."""
import os
import sys
import ansys.edb

from pyedb import __version__
from pyedb.edb_logger import pyedb_logger
from pyedb.generic.general_methods import settings
from ansys.edb.session import launch_session
from pyedb.misc.misc import list_installed_ansysem
from pyedb.generic.general_methods import env_path
from pyedb.generic.general_methods import env_path_student
from pyedb.generic.general_methods import env_value
from pyedb.generic.general_methods import is_linux


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
        self.session = None
        self.server_pid = 0
        if is_linux:  # pragma: no cover
            if env_value(self.edbversion) in os.environ:
                self.base_path = env_path(self.edbversion)
                sys.path.append(self.base_path)
            else:
                main = sys.modules["__main__"]
                edb_path = os.getenv("PYAEDT_SERVER_AEDT_PATH")
                if edb_path:
                    self.base_path = edb_path
                    sys.path.append(edb_path)
                    os.environ[env_value(self.edbversion)] = self.base_path
        else:
            self.base_path = env_path(self.edbversion)
            sys.path.append(self.base_path)
        os.environ["ECAD_TRANSLATORS_INSTALL_DIR"] = self.base_path
        oaDirectory = os.path.join(self.base_path, "common", "oa")
        os.environ["ANSYS_OADIR"] = oaDirectory
        os.environ["PATH"] = "{};{}".format(os.environ["PATH"], self.base_path)
        "Starting grpc server"
        self.session = launch_session(self.base_path, port_num=port)
        if self.session:
            self.server_pid = self.session.local_server_proc.pid
            self.logger.info("Grpc session started")