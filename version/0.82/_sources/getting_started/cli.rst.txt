Command line interface
======================

PyEDB provides a command line interface (CLI) for creating databases, saving changes,
running Python code against an EDB, exporting artifacts, and applying configuration files.

Get started
-----------

To see available commands, run:

.. code-block:: bash

    pyedb --help
    pyaedt edb --help

You can use either ``pyedb <command>`` or ``pyaedt edb <command>``.

All commands support ``--json`` for machine-readable output.

.. code-block:: console

    $ pyedb --json version
    {"status": "ok", "data": {"version": "0.x.y"}}

    $ pyaedt edb --json version
    {"status": "ok", "data": {"version": "0.x.y"}}

Main commands
-------------

The CLI is organized into these top-level commands:

* ``version`` - Show the installed PyEDB version
* ``create`` - Create a new ``.aedb`` database
* ``save`` - Save an EDB in place or as a copy
* ``exec`` - Execute a Python script or inline code against an EDB
* ``attach`` - Open an interactive console attached to an EDB
* ``export`` - Export project artifacts (IPC2581, HFSS/Q3D/Maxwell projects, and more)
* ``config`` - Export/apply/validate configuration files

Common commands
---------------

**Version**

.. code-block:: bash

    pyedb version

**Create a new EDB**

.. code-block:: bash

    pyedb create --path my_board.aedb
    pyedb create --path my_board.aedb --version 2026.1

**Save an existing EDB**

.. code-block:: bash

    pyedb save --path my_board.aedb
    pyedb save --path my_board.aedb --output my_board_copy.aedb

**Run Python against an EDB**

.. code-block:: bash

    pyedb exec my_script.py --path my_board.aedb
    pyedb exec --code "print('hello from pyedb')" --path my_board.aedb

**Open an interactive console**

.. code-block:: bash

    pyedb attach --path my_board.aedb

Export commands
---------------

Use the ``export`` group to generate files from an EDB design.

.. code-block:: bash

    pyedb export ipc2581 --path my_board.aedb --output board.xml
    pyedb export hfss --path my_board.aedb --output out_dir
    pyedb export q3d --path my_board.aedb --output out_dir
    pyedb export maxwell --path my_board.aedb --output out_dir
    pyedb export siwave-dc-results --path my_board.aedb --siwave-project board.siw --solution-name "DC 1"
    pyedb export gds-comp-xml --path my_board.aedb --output control.xml
    pyedb export layout-component --path my_board.aedb --output component.aedbcomp

Configuration commands
----------------------

Use the ``config`` group to work with JSON/TOML configuration files.

.. code-block:: bash

    pyedb config export --path my_board.aedb --output config.json
    pyedb config apply --path my_board.aedb --config config.json
    pyedb config validate --path config.json

Get help
--------

Use ``--help`` on any command group to see available options:

.. code-block:: bash

    pyedb --help
    pyedb export --help
    pyedb config --help
    pyedb exec --help