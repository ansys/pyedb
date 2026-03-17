src.pyedb.dotnet.clr_module
===========================

.. py:module:: src.pyedb.dotnet.clr_module


Attributes
----------

.. autoapisummary::

   src.pyedb.dotnet.clr_module.LINUX_WARNING
   src.pyedb.dotnet.clr_module.existing_showwarning
   src.pyedb.dotnet.clr_module.modules
   src.pyedb.dotnet.clr_module.cpython
   src.pyedb.dotnet.clr_module.is_linux
   src.pyedb.dotnet.clr_module.is_windows
   src.pyedb.dotnet.clr_module.is_clr
   src.pyedb.dotnet.clr_module.pyedb_path
   src.pyedb.dotnet.clr_module.dotnet_root
   src.pyedb.dotnet.clr_module.edb_initialized
   src.pyedb.dotnet.clr_module.win32_client


Functions
---------

.. autoapisummary::

   src.pyedb.dotnet.clr_module.custom_show_warning


Module Contents
---------------

.. py:data:: LINUX_WARNING
   :value: 'Due to compatibility issues between .NET Core and libssl on some Linux versions, for example...


.. py:data:: existing_showwarning

.. py:function:: custom_show_warning(message, category, filename, lineno, file=None, line=None)

   Custom warning used to remove <stdin>:loc: pattern.


.. py:data:: modules

.. py:data:: cpython
   :value: True


.. py:data:: is_linux

.. py:data:: is_windows

.. py:data:: is_clr
   :value: False


.. py:data:: pyedb_path

.. py:data:: dotnet_root
   :value: None


.. py:data:: edb_initialized
   :value: True


.. py:data:: win32_client
   :value: None


