Configuration guides
====================

The configuration system lets you describe PyEDB workflows either as a
file-oriented payload or through a Python builder API.

Use this section to choose the view that best matches how you work:

* :doc:`file_architecture` explains the serialized JSON and TOML structure,
  supported sections, and field intent.
* :doc:`configuration_api_guide` is the API guide: core objects, section
  mapping, session-aware ``get()`` helpers, persist methods, and a complete
  example incorporating all recent additions.
* :doc:`configuration_api_examples` provides hands-on worked examples covering
  ports, setups, padstacks, stackup, modeler geometry, and more.

.. grid:: 3

    .. grid-item-card:: Configuration file architecture :fa:`file-code`
        :link: file_architecture
        :link-type: doc

        Understand the JSON and TOML schema, supported sections, and how
        configuration data is applied to a design.

    .. grid-item-card:: Configuration API guide :fa:`code`
        :link: configuration_api_guide
        :link-type: doc

        Core objects, session-aware ``get()`` helpers, persist methods
        (``save_to_json`` / ``to_json``), and a complete end-to-end example.

    .. grid-item-card:: Practical examples :fa:`flask`
        :link: configuration_api_examples
        :link-type: doc

        Thirteen worked examples from coax ports and wave ports to stackup
        materials and modeler geometry — with inline commentary.


.. toctree::
    :hidden:
    :maxdepth: 2

    file_architecture
    configuration_api_guide
    configuration_api_examples
    ../autoapi/pyedb/configuration/index

