# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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
import sys

from ansys.edb.core.session import launch_session
import psutil

from pyedb import __version__
from pyedb.edb_logger import pyedb_logger
from pyedb.generic.general_methods import env_path, env_value, is_linux
from pyedb.misc.misc import list_installed_ansysem


class RpcSession:
    """Static Class managing RPC server."""

    server_pid = 0
    rpc_session = None
    base_path = None
    port = 10000

    @staticmethod
    def start(edb_version, port, restart_server=False):
        """Start RPC-server, the server must be started before opening EDB.

        Parameters
        ----------
        edb_version : str, optional.
            Specify the Ansys version. If None, the latest installation will be detected on the local machine.

        port : int
            Port number used for the RPC session.

        restart_server : bool, optional.
            Force restarting the RPC server by killing the process in case EDB_RPC is already started. All open EDB
            connection will be lost. This option must be used at the beginning of an application only to ensure the
            server is properly started.
        """
        RpcSession.port = port
        if not edb_version:  # pragma: no cover
            try:
                edb_version = "20{}.{}".format(list_installed_ansysem()[0][-3:-1], list_installed_ansysem()[0][-1:])
                pyedb_logger.info("Edb version " + edb_version)
            except IndexError:
                raise Exception("No ANSYSEM_ROOTxxx is found.")
        pyedb_logger.info("Logger is initialized in EDB.")
        pyedb_logger.info("legacy v%s", __version__)
        pyedb_logger.info("Python version %s", sys.version)
        if is_linux:
            if env_value(edb_version) in os.environ:
                RpcSession.base_path = env_path(edb_version)
                sys.path.append(RpcSession.base_path)
            else:
                edb_path = os.getenv("PYAEDT_SERVER_AEDT_PATH")
                if edb_path:
                    RpcSession.base_path = edb_path
                    sys.path.append(edb_path)
                    os.environ[env_value(edb_version)] = RpcSession.base_path
        else:
            RpcSession.base_path = env_path(edb_version)
            sys.path.append(RpcSession.base_path)
        os.environ["ECAD_TRANSLATORS_INSTALL_DIR"] = RpcSession.base_path
        oa_directory = os.path.join(RpcSession.base_path, "common", "oa")
        os.environ["ANSYS_OADIR"] = oa_directory
        os.environ["PATH"] = "{};{}".format(os.environ["PATH"], RpcSession.base_path)

        if RpcSession.server_pid:
            if restart_server:
                pyedb_logger.logger.info("Restarting RPC server")
                RpcSession.kill()
                RpcSession.__start_rpc_server()
            else:
                pyedb_logger.info(f"Server already running on port {RpcSession.port}")
        else:
            RpcSession.__start_rpc_server()
            if RpcSession.rpc_session:
                RpcSession.server_pid = RpcSession.rpc_session.local_server_proc.pid
                pyedb_logger.info(f"Grpc session started: pid={RpcSession.server_pid}")
            else:
                pyedb_logger.error("Failed to start EDB_RPC_server process")

    @staticmethod
    def __get_process_id():
        proc = [p for p in list(psutil.process_iter()) if "edb_rpc" in p.name().lower()]
        if proc:
            RpcSession.server_pid = proc[0].pid
        else:
            RpcSession.server_pid = 0

    @staticmethod
    def __start_rpc_server():
        RpcSession.rpc_session = launch_session(RpcSession.base_path, port_num=RpcSession.port)
        if RpcSession.rpc_session:
            RpcSession.server_pid = RpcSession.rpc_session.local_server_proc.pid
            pyedb_logger.logger.info("Grpc session started")

    @staticmethod
    def __kill():
        p = psutil.Process(RpcSession.server_pid)
        p.terminate()

    @staticmethod
    def close():
        """Terminate the current RPC session. Must be executed at the end of the script to close properly the session.
        If not executed, users should force restarting the process using the flag `restart_server`=`True`.
        """
        if RpcSession.rpc_session:
            RpcSession.rpc_session.disconnect()
