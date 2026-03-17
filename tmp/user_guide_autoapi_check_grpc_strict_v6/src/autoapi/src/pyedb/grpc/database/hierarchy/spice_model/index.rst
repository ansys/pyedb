src.pyedb.grpc.database.hierarchy.spice_model
=============================================

.. py:module:: src.pyedb.grpc.database.hierarchy.spice_model


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.hierarchy.spice_model.SpiceModel


Module Contents
---------------

.. py:class:: SpiceModel(component, name=None, file_path=None, sub_circuit=None)

   Manage :class:`SpiceModel <ansys.edb.core.hierarchy.spice_model.SpiceModel>`


   .. py:property:: name
      :type: str


      SPICE model name.

      Returns
      -------
      str
          SPICE model name.




   .. py:property:: model_name

      Model name.

      .. deprecated:: 0.70.0
              Use :attr:`name` instead.

      Returns
      -------
      str
          Model name.




   .. py:property:: spice_file_path


   .. py:property:: file_path

      SPICE file path.

      Returns
      -------
      str
          SPICE file path.




