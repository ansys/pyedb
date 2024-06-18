# -*- coding: utf-8 -*-
from decimal import Decimal
import json
import math
import random
import re
import string

from pyedb.generic.general_methods import settings


def format_decimals(el):  # pragma: no cover
    """

    Parameters
    ----------
    el :


    Returns
    -------

    """
    if float(el) > 1000:
        num = "{:,.0f}".format(Decimal(el))
    elif float(el) > 1:
        num = "{:,.3f}".format(Decimal(el))
    else:
        num = "{:.3E}".format(Decimal(el))
    return num


def random_string(length=6, only_digits=False, char_set=None):  # pragma: no cover
    """Generate a random string

    Parameters
    ----------
    length :
        length of the random string (Default value = 6)
    only_digits : bool, optional
        ``True`` if only digits are to be included.
    char_set : str, optional
        Custom character set to pick the characters from.  By default chooses from
        ASCII and digit characters or just digits if ``only_digits`` is ``True``.

    Returns
    -------
    type
        random string

    """
    if not char_set:
        if only_digits:
            char_set = string.digits
        else:
            char_set = string.ascii_uppercase + string.digits
    random_str = "".join(random.choice(char_set) for _ in range(int(length)))
    return random_str


def unique_string_list(element_list, only_string=True):  # pragma: no cover
    """Return a unique list of strings from an element list.

    Parameters
    ----------
    element_list :

    only_string :
         (Default value = True)

    Returns
    -------

    """
    if element_list:
        if isinstance(element_list, list):
            element_list = set(element_list)
        elif isinstance(element_list, str):
            element_list = [element_list]
        else:
            error_message = "Invalid list data"
            try:
                error_message += " {}".format(element_list)
            except:
                pass
            raise Exception(error_message)

        if only_string:
            non_string_entries = [x for x in element_list if type(x) is not str]
            assert not non_string_entries, "Invalid list entries {} are not a string!".format(non_string_entries)

    return element_list


def string_list(element_list):  # pragma: no cover
    """

    Parameters
    ----------
    element_list :


    Returns
    -------

    """
    if isinstance(element_list, str):
        element_list = [element_list]
    else:
        assert isinstance(element_list, str), "Input must be a list or a string"
    return element_list


def ensure_list(element_list):  # pragma: no cover
    """

    Parameters
    ----------
    element_list :


    Returns
    -------

    """
    if not isinstance(element_list, list):
        element_list = [element_list]
    return element_list


def from_rkm(code):  # pragma: no cover
    """Convert an RKM code string to a string with a decimal point.

    Parameters
    ----------
    code : str
        RKM code string.

    Returns
    -------
    str
        String with a decimal point and an R value.

    Examples
    --------
    >>> from_rkm('R47')
    '0.47'

    >>> from_rkm('4R7')
    '4.7'

    >>> from_rkm('470R')
    '470'

    >>> from_rkm('4K7')
    '4.7k'

    >>> from_rkm('47K')
    '47k'

    >>> from_rkm('47K3')
    '47.3k'

    >>> from_rkm('470K')
    '470k'

    >>> from_rkm('4M7')
    '4.7M'

    """

    # Matches RKM codes that start with a digit.
    # fd_pattern = r'([0-9]+)([LREkKMGTFmuµUnNpP]+)([0-9]*)'
    fd_pattern = r"([0-9]+)([{}]+)([0-9]*)".format(
        "".join(RKM_MAPS.keys()),
    )
    # matches rkm codes that end with a digit
    # ld_pattern = r'([0-9]*)([LREkKMGTFmuµUnNpP]+)([0-9]+)'
    ld_pattern = r"([0-9]*)([{}]+)([0-9]+)".format("".join(RKM_MAPS.keys()))

    fd_regex = re.compile(fd_pattern, re.I)
    ld_regex = re.compile(ld_pattern, re.I)

    for regex in [fd_regex, ld_regex]:
        m = regex.match(code)
        if m:
            fd, base, ld = m.groups()
            ps = RKM_MAPS[base]

            if ld:
                return_str = "".join([fd, ".", ld, ps])
            else:
                return_str = "".join([fd, ps])
            return return_str
    return code


def str_to_bool(s):  # pragma: no cover
    """Convert a ``"True"`` or ``"False"`` string to its corresponding Boolean value.

    If the passed arguments are not relevant in the context of conversion, the argument
    itself is returned. This method can be called using the ``map()`` function to
    ensure conversion of Boolean strings in a list.

    Parameters
    ----------
    s: str

    Returns
    -------
    bool or str
         The method is not case-sensitive.
         - ``True`` is returned  if the input is ``"true"``, ``"1"``,
           `"yes"``, or ``"y"``,
         - ``False`` is returned if the input is ``"false"``, ``"no"``,
           ``"n``,  or ``"0"``.
         - Otherwise, the input value is passed through the method unchanged.

    """
    if type(s) == str:
        if s.lower() in ["true", "yes", "y", "1"]:
            return True
        elif s.lower() in ["false", "no", "n", "0"]:
            return False
        else:
            return s
    elif type(s) == int:
        return False if s == 0 else True


unit_val = {
    "": 1.0,
    "uV": 1e-6,
    "mV": 1e-3,
    "V": 1.0,
    "kV": 1e3,
    "MegV": 1e6,
    "ns": 1e-9,
    "us": 1e-6,
    "ms": 1e-3,
    "s": 1.0,
    "min": 60,
    "hour": 3600,
    "rad": 1.0,
    "deg": math.pi / 180,
    "Hz": 1.0,
    "kHz": 1e3,
    "MHz": 1e6,
    "nm": 1e-9,
    "um": 1e-6,
    "mm": 1e-3,
    "in": 0.0254,
    "inches": 0.0254,
    "mil": 2.54e-5,
    "cm": 1e-2,
    "dm": 1e-1,
    "meter": 1.0,
    "km": 1e3,
}


def float_units(val_str, units=""):  # pragma: no cover
    """Retrieve units for a value.

    Parameters
    ----------
    val_str : str
        Name of the float value.

    units : str, optional
         The default is ``""``.

    Returns
    -------

    """
    if not units in unit_val:
        raise Exception("Specified unit string " + units + " not known!")

    loc = re.search("[a-zA-Z]", val_str)
    try:
        b = loc.span()[0]
        var = [float(val_str[0:b]), val_str[b:]]
        val = var[0] * unit_val[var[1]]
    except:
        val = float(val_str)

    val = val / unit_val[units]
    return val


def json_to_dict(fn):  # pragma: no cover
    """Load Json File to a dictionary.

    Parameters
    ----------
    fn : str
        json file full path.

    Returns
    -------
    dict
    """
    json_data = {}
    with open(fn) as json_file:
        try:
            json_data = json.load(json_file)
        except json.JSONDecodeError as e:  # pragma: no cover
            error = "Error reading json: {} at line {}".format(e.msg, e.lineno)
            settings.logger.error(error)
    return json_data
