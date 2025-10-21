# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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
import secrets
import sys
import time

from ansys.edb.core.session import launch_session
from ansys.edb.core.utility.io_manager import (
    IOMangementType,
    end_managing,
    start_managing,
)
import psutil

from pyedb import __version__
from pyedb.generic.general_methods import env_path, env_value, is_linux
from pyedb.generic.settings import settings
from pyedb.misc.misc import list_installed_ansysem

latency_delay = 0.1


class RpcSession:
    """Static Class managing RPC server."""

    pid = 0
    rpc_session = None
    base_path = None
    port = 10000

    @staticmethod
    def start(edb_version, port=0, restart_server=False):
        """Start RPC-server, the server must be started before opening EDB.

        Parameters
        ----------
        edb_version : str, optional.
            Specify ANSYS version.
            If None, the latest installation will be detected on the local machine.

        port : int, optional
            Port number used for the RPC session.
            If not provided, a random free port is automatically selected.

        restart_server : bool, optional.
            Force restarting the RPC server by killing the process in case EDB_RPC is already started.
            All open EDB
            connection will be lost.
            This option must be used at the beginning of an application only to ensure the
            server is properly started.
        kill_all_instances : bool, optional.
            Force killing all RPC sever instances, including a zombie process.
            To be used with caution, default value is `False`.
        """
        if not port:
            RpcSession.port = RpcSession.__get_random_free_port()
        else:
            RpcSession.port = port
        if not edb_version:  # pragma: no cover
            try:
                edb_version = "20{}.{}".format(list_installed_ansysem()[0][-3:-1], list_installed_ansysem()[0][-1:])
                settings.logger.info("Edb version " + edb_version)
            except IndexError:
                raise Exception("No ANSYSEM_ROOTxxx is found.")
        settings.logger.info("Logger is initialized in EDB.")
        settings.logger.info("legacy v%s", __version__)
        settings.logger.info("Python version %s", sys.version)
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

        if RpcSession.pid:
            if restart_server:
                settings.logger.logger.info("Restarting RPC server")
                RpcSession.kill()
                RpcSession.__start_rpc_server()
            else:
                settings.logger.info(f"Server already running on port {RpcSession.port}")
        else:
            RpcSession.__start_rpc_server()
            if RpcSession.rpc_session:
                RpcSession.server_pid = RpcSession.rpc_session.local_server_proc.pid
                settings.logger.info(f"Grpc session started: pid={RpcSession.server_pid}")
            else:
                settings.logger.error("Failed to start EDB_RPC_server process")

    @staticmethod
    def __get_process_id():
        proc = [p for p in list(psutil.process_iter()) if "edb_rpc" in p.name().lower()]
        time.sleep(latency_delay)
        if proc:
            RpcSession.pid = proc[-1].pid
        else:
            RpcSession.pid = 0

    @staticmethod
    def __start_rpc_server():
        RpcSession.rpc_session = launch_session(RpcSession.base_path, port_num=RpcSession.port)
        start_managing(IOMangementType.READ_AND_WRITE)
        time.sleep(latency_delay)
        if RpcSession.rpc_session:
            RpcSession.pid = RpcSession.rpc_session.local_server_proc.pid
            settings.logger.logger.info("Grpc session started")

    @staticmethod
    def kill():
        p = psutil.Process(RpcSession.pid)
        time.sleep(latency_delay)
        try:
            p.terminate()
            print(f"RPC session pid: {RpcSession.pid} killed due to execution failure.")
            RpcSession.pid = 0
        except:
            print("RPC session closed.")

    @staticmethod
    def kill_all_instances():
        # collect PIDs safely
        proc = []
        for p in psutil.process_iter(["pid", "name"]):
            try:
                if "edb_rpc" in p.info["name"].lower():
                    proc.append(p.info["pid"])
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        time.sleep(latency_delay)

        # terminate gracefully
        for pid in proc:
            try:
                p = psutil.Process(pid)
                p.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    @staticmethod
    def close():
        """Terminate the current RPC session. Must be executed at the end of the script to close properly the session.
        If not executed, users should force restarting the process using the flag `restart_server`=`True`.
        """
        if RpcSession.rpc_session:
            end_managing()
            RpcSession.rpc_session.disconnect()
            time.sleep(latency_delay)
            RpcSession.__get_process_id()

    @staticmethod
    def __get_random_free_port():
        """"""
        secure_random = secrets.SystemRandom()
        port = secure_random.randint(49152, 65535)
        while True:
            used_ports = [conn.laddr[1] for conn in psutil.net_connections()]
            if port in used_ports:
                port = secure_random.randint(49152, 65535)
            else:
                break
        return port
