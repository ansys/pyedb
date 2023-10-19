"""
Unit Test Configuration Module
-------------------------------

Description
===========

This module contains the configuration and fixture for the pytest-based tests for pyedb.

The default configuration can be changed by placing a file called local_config.json in the same
directory as this module. An example of the contents of local_config.json
{
  "desktopVersion": "2022.2",
  "NonGraphical": false,
  "NewThread": false,
}

"""

from pyaedt.misc.misc import list_installed_ansysem


# Initialize default desktop configuration
default_version = "2023.2"
if "ANSYSEM_ROOT{}".format(default_version[2:].replace(".", "")) not in list_installed_ansysem():
    default_version = list_installed_ansysem()[0][12:].replace(".", "")
    default_version = "20{}.{}".format(default_version[:2], default_version[-1])
