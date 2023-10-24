PyEDB documentation  |version|
==============================

PyEDB is a Python library that interacts directly with the EDB-core API to make scripting simpler.

.. grid:: 2

   .. grid-item-card::
            :img-top: _static/assets/index_getting_started.png

            Getting started
            ^^^^^^^^^^^^^^^

            Learn how to run install PyEDB.

            +++

            .. button-link:: Getting_started/index.html
               :color: secondary
               :expand:
               :outline:
               :click-parent:

                  Getting started

   .. grid-item-card::
            :img-top: _static/assets/index_user_guide.png

            User guide
            ^^^^^^^^^^

            Understand key concepts and approaches for primitives,
            modeler, mesh, setup and post-processing.

            +++
            .. button-link:: User_guide/index.html
               :color: secondary
               :expand:
               :outline:
               :click-parent:

                  User guide



   .. grid-item-card::
            :img-top: _static/assets/index_api.png

            EDB API reference
            ^^^^^^^^^^^^^^^^^

            Understand PyAEDT EDB API endpoints, their capabilities,
            and how to interact with them programmatically.

            +++
            .. button-link:: EDBAPI/index.html
               :color: secondary
               :expand:
               :outline:
               :click-parent:

                  EDB API reference

.. jinja:: main_toctree

    .. grid:: 2

           {% if run_examples %}
           .. grid-item-card::
                    :img-top: _static/assets/index_examples.png

                    Examples
                    ^^^^^^^^

                    Explore examples that show how to use PyEDB to
                    perform different types of simulations.

                    +++
                    .. button-link:: examples/index.html
                       :color: secondary
                       :expand:
                       :outline:
                       :click-parent:

                          Examples
           {% endif %}

        .. grid-item-card::
                :img-top: _static/assets/index_contribute.png

                Contribute
                ^^^^^^^^^^
                Learn how to contribute to the PyAEDT codebase
                or documentation.

                +++
                .. button-link:: Getting_started/Contributing.html
                   :color: secondary
                   :expand:
                   :outline:
                   :click-parent:

                      Contribute

Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. jinja:: main_toctree

    .. toctree::
       :hidden:

       Getting_started/index
       User_guide/index
       EDBAPI/index
       {% if run_examples %}
       examples/index
       {% endif %}


