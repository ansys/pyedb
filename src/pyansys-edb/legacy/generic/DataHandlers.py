# -*- coding: utf-8 -*-
from collections import OrderedDict
from decimal import Decimal
import json
import math
import random
import re
import string

from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.generic.general_methods import settings
from pyaedt.modeler.cad.elements3d import EdgePrimitive
from pyaedt.modeler.cad.elements3d import FacePrimitive
from pyaedt.modeler.cad.elements3d import VertexPrimitive


def create_list_for_csharp(input_list, return_strings=False):
    """

    Parameters
    ----------
    input_list :

    return_strings :
         (Default value = False)

    Returns
    -------

    """
    from pyaedt.generic.clr_module import Double
    from pyaedt.generic.clr_module import List

    if return_strings:
        col = List[str]()
    else:
        col = List[Double]()

    for el in input_list:
        if return_strings:
            col.Add(str(el))
        else:
            col.Add(el)
    return col


@pyaedt_function_handler()
def create_table_for_csharp(input_list_of_list, return_strings=True):
    """

    Parameters
    ----------
    input_list_of_list :

    return_strings :
         (Default value = True)

    Returns
    -------

    """
    from pyaedt.generic.clr_module import List

    new_table = List[List[str]]()
    for col in input_list_of_list:
        newcol = create_list_for_csharp(col, return_strings)
        new_table.Add(newcol)
    return new_table
