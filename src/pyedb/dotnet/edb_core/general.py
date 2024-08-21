# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
This module contains EDB general methods and related methods.

"""

from __future__ import absolute_import  # noreorder

import logging

from pyedb.dotnet.clr_module import Dictionary, List, Tuple

try:
    from enum import Enum
except ImportError:
    Enum = None


logger = logging.getLogger(__name__)


def convert_netdict_to_pydict(dict_in):
    """Convert a net dictionary to a Python dictionary.

    Parameters
    ----------
    dict_in : dict
        Net dictionary to convert.

    Returns
    -------
    dict
        Dictionary converted to Python.

    """
    pydict = {}
    for key in dict_in.Keys:
        pydict[key] = dict_in[key]
    return pydict


def convert_pytuple_to_nettuple(_tuple):
    """Convert a Python tuple into a .NET tuple.
    Parameters
    ----------
    tuple : Python tuple

    Returns
    -------
    .NET tuple.
    """
    return Tuple.Create(_tuple[0], _tuple[1])


def convert_pydict_to_netdict(input_dict):
    """Convert a Python dictionary to a .NET dictionary.

    Parameters
    ----------
    input_dict : dict
        Python dictionary to convert.


    Returns
    -------
    dict
        Dictionary converted to .NET.
    """
    net_dict = Dictionary[type(list(input_dict.keys())[0]), type(list(input_dict.values())[0])]()
    for k1, v1 in input_dict.items():  # pragma: no cover
        net_dict[k1] = v1
    return net_dict
    # to be completed


def convert_py_list_to_net_list(pylist, list_type=None):
    """Convert a Python list to a Net list.

    Parameters
    ----------
    pylist : list
        Python list to convert.

    Returns
    -------
    list
        List converted to Net.
    """
    if not isinstance(pylist, (list, tuple)):
        pylist = [pylist]
    ls = list([type(item) for item in pylist])
    if len(ls) > 0:
        if list_type:
            net_list = List[list_type]()
        else:
            net_list = List[ls[0]]()
        for el in pylist:
            net_list.Add(el)
        return net_list


def convert_net_list_to_py_list(netlist):
    """Convert a Net list to a Python list.

    Parameters
    ----------
    netlist : list
       Net list to convert.


    Returns
    -------
    list
        List converted to Python.
    """
    pylist = []
    for el in netlist:
        pylist.__add__(el)
    return pylist


class PadGeometryTpe(Enum):  # pragma: no cover
    Circle = 1
    Square = 2
    Rectangle = 3
    Oval = 4
    Bullet = 5
    NSidedPolygon = 6
    Polygon = 7
    Round45 = 8
    Round90 = 9
    Square45 = 10
    Square90 = 11
    InvalidGeometry = 12


class DielectricExtentType(Enum):
    BoundingBox = 0
    Conforming = 1
    ConvexHull = 2
    Polygon = 3


class Primitives(Enum):
    Rectangle = 0
    Circle = 1
    Polygon = 2
    Path = 3
    Bondwire = 4
    PrimitivePlugin = 5
    Text = 6
    Path3D = 7
    BoardBendDef = 8
    InValidType = 9


class LayoutObjType(Enum):
    InvalidLayoutObj = -1
    Primitive = 0
    PadstackInstance = 1
    Terminal = 2
    TerminalInstance = 3
    CellInstance = 4
    Layer = 5
    Net = 6
    Padstack = 7
    Group = 8
    NetClass = 9
    Cell = 10
    DifferentialPair = 11
    PinGroup = 12
    VoltageRegulator = 13
    ExtendedNet = 14
    LayoutObjTypeCount = 15
