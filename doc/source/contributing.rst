.. _contributing_pyedb:

==========
Contribute
==========
Overall guidance on contributing to a PyAnsys repository appears in
`Contribute <https://dev.docs.pyansys.com/how-to/contributing.html>`_
in the *PyAnsys Developer's Guide*. Ensure that you are thoroughly familiar
with this guide before attempting to contribute to PyEDB.

The following contribution information is specific to PyEDB.

Clone the repository
--------------------
To clone and install the latest version of PyEDB in
development mode, run these commands:

.. code::

    git clone https://github.com/ansys/pyedb
    cd pyedb
    python -m pip install --upgrade pip
    pip install -e .

Post issues
-----------
Use the `PyEDB Issues <https://github.com/ansys/pyedb/issues>`_
page to submit questions, report bugs, and request new features.

To reach the product support team, email `pyansys.core@ansys.com <pyansys.core@ansys.com>`_.

View PyEDB documentation
-------------------------
Documentation for the latest stable release of PyEDB is hosted at
`PyEDB documentation <https://edb.docs.pyansys.com>`_.

In the upper right corner of the documentation's title bar, there is an option
for switching from viewing the documentation for the latest stable release
to viewing the documentation for the development version or previously
released versions.

Adhere to code style
--------------------
PyEDB is compliant with `PyAnsys code style
<https://dev.docs.pyansys.com/coding_style/index.html>`_. It uses the tool
`pre-commit <https://pre-commit.com/>`_ to check the code style. You can install
and activate this tool with these commands:

.. code:: bash

  pip install pre-commit
  pre-commit run --all-files

You can also install this as a pre-commit hook with this command:

.. code:: bash

  pre-commit install

This way, it's not possible for you to push code that fails the style checks.
For example::

  $ pre-commit install
  $ git commit -am "Add my cool feature."
  black....................................................................Passed
  isort (python)...........................................................Passed
  flake8...................................................................Passed
  codespell................................................................Passed
  fix requirements.txt.....................................................Passed
  blacken-docs.............................................................Passed

Log errors
~~~~~~~~~~
PyEDB has an internal logging tool named ``Messenger``
and a log file that is automatically generated in the project
folder.

The following examples show how ``Messenger`` is used to
write both to the internal AEDT message windows and the log file:

.. code:: python

    self.logger.error("This is an error message.")
    self.logger.warning("This is a warning message.")
    self.logger.info("This is an info message.")

These examples show how to write messages only to the log file:

.. code:: python

    self.logger.error("This is an error message.")
    self.logger.warning("This is a warning message.")
    self.logger.info("This is an info message.")


Hard-coded values
~~~~~~~~~~~~~~~~~~
Do not write hard-coded values to the registry. Instead, use the Configuration service.

Maximum line length
~~~~~~~~~~~~~~~~~~~
Best practice is to keep the length at or below 120 characters for code
and comments. Lines longer than this might not display properly on some terminals
and tools or might be difficult to follow.
