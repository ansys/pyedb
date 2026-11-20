.. _hfss_log_parser_api:

==================================================================
HFSS log parser -- ``pyedb.workflows.utilities.hfss_log_parser``
==================================================================

.. automodule:: pyedb.workflows.utilities.hfss_log_parser
   :no-members:
   :noindex:


Top-level façade
----------------

.. autoclass:: HFSSLogParser
   :members:
   :special-members: __init__
   :show-inheritance:


Aggregated result object
------------------------

.. autoclass:: ParsedLog
   :members:
   :exclude-members: __dataclass_fields__,__dataclass_params__,__post_init__
   :show-inheritance:


Data containers
---------------

.. autoclass:: ProjectInfo
   :members:
   :exclude-members: __dataclass_fields__,__dataclass_params__,__post_init__
   :show-inheritance:

.. autoclass:: InitMesh
   :members:
   :exclude-members: __dataclass_fields__,__dataclass_params__,__post_init__
   :show-inheritance:

.. autoclass:: AdaptivePass
   :members:
   :exclude-members: __dataclass_fields__,__dataclass_params__,__post_init__
   :show-inheritance:

.. autoclass:: Sweep
   :members:
   :exclude-members: __dataclass_fields__,__dataclass_params__,__post_init__
   :show-inheritance:


Block parsers (advanced usage)
------------------------------

.. autoclass:: ProjectBlockParser
   :members:
   :special-members: __init__
   :show-inheritance:

.. autoclass:: InitMeshBlockParser
   :members:
   :special-members: __init__
   :show-inheritance:

.. autoclass:: AdaptiveBlockParser
   :members:
   :special-members: __init__
   :show-inheritance:

.. autoclass:: SweepBlockParser
   :members:
   :special-members: __init__
   :show-inheritance:


Base class
~~~~~~~~~~

.. autoclass:: BlockParser
   :members:
   :special-members: __init__
   :show-inheritance:


Utility helpers
---------------

The functions below are private by convention (leading underscore) but are
exposed in the documentation for contributors and advanced users.

.. autofunction:: _to_hz

.. autofunction:: _to_sec

.. autofunction:: _as_dict