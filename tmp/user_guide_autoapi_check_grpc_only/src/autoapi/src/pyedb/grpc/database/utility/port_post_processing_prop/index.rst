src.pyedb.grpc.database.utility.port_post_processing_prop
=========================================================

.. py:module:: src.pyedb.grpc.database.utility.port_post_processing_prop


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.utility.port_post_processing_prop.PortPostProcessingProp


Module Contents
---------------

.. py:class:: PortPostProcessingProp(core)

   Port post-processing properties.

   This class wraps the gRPC port post-processing properties, providing access to
   deembedding length, renormalization impedance, voltage magnitude and phase,
   and flags for deembedding and renormalization.

   Parameters
   ----------
   core : GrpcPortPostProcessing
       The underlying gRPC port post-processing object.


   .. py:attribute:: core


   .. py:property:: deembed_length

      Deembedding length.

      Returns
      -------
      float
          The deembedding length value.



   .. py:property:: renormalization_impedance

      Renormalization impedance.

      Returns
      -------
      float
          The renormalization impedance value.



   .. py:property:: voltage_magnitude

      Voltage magnitude.

      Returns
      -------
      float
          The voltage magnitude value.



   .. py:property:: voltage_phase

      Voltage phase.

      Returns
      -------
      float
          The voltage phase value.



   .. py:property:: do_deembed

      Whether to perform deembedding.

      Returns
      -------
      bool
          True if deembedding is enabled, False otherwise.



   .. py:property:: do_renormalize

      Whether to perform renormalization.

      Returns
      -------
      bool
          True if renormalization is enabled, False otherwise.



