src.pyedb.workflows.utilities.physical_merge
============================================

.. py:module:: src.pyedb.workflows.utilities.physical_merge


Attributes
----------

.. autoapisummary::

   src.pyedb.workflows.utilities.physical_merge.layer_mapping
   src.pyedb.workflows.utilities.physical_merge.cache_padstack_def
   src.pyedb.workflows.utilities.physical_merge.cache_layers


Functions
---------

.. autoapisummary::

   src.pyedb.workflows.utilities.physical_merge.physical_merge


Module Contents
---------------

.. py:data:: layer_mapping

.. py:data:: cache_padstack_def

.. py:data:: cache_layers

.. py:function:: physical_merge(hosting_edb, merged_edb: Union[str, pyedb.Edb], on_top=True, vector=(0.0, 0.0), prefix='merged_', show_progress: bool = True) -> bool

   Merge two EDBs together by copying the primitives from the merged_edb into the hosting_edb.

   Parameters
   ----------
   hosting_edb : Edb
       The EDB that will host the merged primitives.
   merged_edb : str, Edb
       Aedb folder path or The EDB that will be merged into the hosting_edb.
   on_top : bool, optional
       If True, the primitives from the merged_edb will be placed on top of the hosting_edb primitives.
       If False, they will be placed below. Default is True.
   vector : tuple, optional
       A tuple (x, y) representing the offset to apply to the primitives from the merged. Default is (0.0, 0.0).
   prefix : str, optional
       A prefix to add to the layer names of the merged primitives to avoid name clashes. Default is "merged_."
   show_progress : bool, optional
       If True, print progress to stdout during long operations (primitives/padstacks merging). Default is True.

   Returns
   -------
   bool
       True if the merge was successful, False otherwise.



