Configuration guides
====================

The configuration system lets you describe PyEDB workflows either as a
file-oriented payload or through a Python builder API.

Use this section to choose the view that best matches how you work:

* :doc:`file_architecture` explains the serialized JSON and TOML structure,
  supported sections, and field intent.
* :doc:`cfg_api_guide` shows how to build the same payload programmatically
  with :mod:`pyedb.configuration.cfg_api`.

.. grid:: 2

    .. grid-item-card:: Configuration file architecture :fa:`file-code`
        :link: file_architecture
        :link-type: doc

        Understand the JSON and TOML schema, supported sections, and how
        configuration data is applied to a design.

    .. grid-item-card:: Configuration API guide :fa:`code`
        :link: cfg_api_guide
        :link-type: doc

        Learn how to build, serialize, and apply complete configuration
        payloads from Python.


.. toctree::
    :hidden:
    :maxdepth: 1

    file_architecture
    cfg_api_guide
    ../autoapi/pyedb/configuration/cfg_api/index

