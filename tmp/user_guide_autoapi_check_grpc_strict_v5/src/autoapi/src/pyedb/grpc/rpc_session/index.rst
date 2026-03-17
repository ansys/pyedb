src.pyedb.grpc.rpc_session
==========================

.. py:module:: src.pyedb.grpc.rpc_session


Attributes
----------

.. autoapisummary::

   src.pyedb.grpc.rpc_session.latency_delay


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.rpc_session.RpcSession


Module Contents
---------------

.. py:data:: latency_delay
   :value: 0.1


.. py:class:: RpcSession

   Static Class managing RPC server.


   .. py:attribute:: pid
      :value: 0



   .. py:attribute:: rpc_session
      :value: None



   .. py:attribute:: base_path
      :value: None



   .. py:attribute:: port
      :value: 10000



   .. py:method:: start(edb_version, port=0, restart_server=False)
      :staticmethod:


      Start RPC-server, the server must be started before opening EDB.

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



   .. py:method:: kill()
      :staticmethod:



   .. py:method:: kill_all_instances()
      :staticmethod:



   .. py:method:: close()
      :staticmethod:


      Terminate the current RPC session. Must be executed at the end of the script to close properly the session.
      If not executed, users should force restarting the process using the flag `restart_server`=`True`.



