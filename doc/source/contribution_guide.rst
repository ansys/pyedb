Contribution Guide
==================

All contributions to PyEDB are welcome. This guide will help you get started.

Development Environment Setup
-----------------------------
1.  Fork the `PyEDB repository <https://github.com/ansys/pyedb>`_ on GitHub.
2.  Clone your fork locally:

    .. code-block:: bash

        git clone https://github.com/your-username/pyedb.git
        cd pyedb

3.  Install the package in development mode with all dependencies:

    .. code-block:: bash

        pip install -e ".[dev]"

4.  Install pre-commit hooks to ensure code quality:

    .. code-block:: bash

        pre-commit install

Running Tests
-------------
To ensure your changes don't break existing functionality, run the test suite:

.. code-block:: bash

    pytest tests/ -v

Building Documentation
----------------------
To build and preview the documentation locally:

.. code-block:: bash

    cd doc
    make html
    # Open _build/html/index.html in your browser

Submission Process
------------------
1.  Create a branch for your feature or bug fix: `git checkout -b feature/your-feature-name`
2.  Make your changes and add tests.
3.  Ensure all tests pass and pre-commit checks are satisfied.
4.  Commit your changes: `git commit -m "Add feature: your feature description"`
5.  Push to your fork: `git push origin feature/your-feature-name`
6.  Open a Pull Request against the main PyEDB repository.

Code Style
----------
*   Follow `PEP 8 <https://pep8.org/>`_ guidelines.
*   Use Google-style docstrings for all public functions and classes.
*   Include type hints for all function parameters and return values.

Documentation Contributions
---------------------------
When adding new features, please also update the relevant documentation:

*   Add examples to the appropriate section in `user_guide/common_tasks.rst`.
*   Create a new Jupyter notebook in `doc/notebooks/` if the feature warrants a comprehensive example.
*   Ensure all new public API elements have proper docstrings.