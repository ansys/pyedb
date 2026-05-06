# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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

from pyedb.dotnet.database.cell.terminal.edge_terminal import EdgeTerminal
from pyedb.dotnet.database.cell.terminal.terminal import Terminal
from pyedb.dotnet.database.general import convert_py_list_to_net_list


class BundleTerminal(Terminal):
    """Manages bundle terminal properties.

    Parameters
    ----------
    pedb : pyedb.edb.Edb
        EDB object from the ``Edblib`` library.
    edb_object : Ansys.Ansoft.Edb.Cell.Terminal.BundleTerminal
        BundleTerminal instance from EDB.
    """

    def __init__(self, pedb, edb_object):
        super().__init__(pedb, edb_object)

    @property
    def terminals(self):
        """Get terminals belonging to this excitation."""
        return [EdgeTerminal(self._pedb, i) for i in list(self._edb_object.GetTerminals())]

    def decouple(self):
        """Ungroup a bundle of terminals."""
        return self._edb_object.Ungroup()

    @classmethod
    def create(cls, pedb, name="", terminals=None) -> "BundleTerminal":
        """
        Create a new bundle terminal from a collection of individual terminals.

        A bundle terminal groups multiple terminals (edge terminals, padstack instance
        terminals, or other terminal types) into a single logical entity. This is useful
        for creating multi-pin ports, differential pairs, or complex port definitions
        where multiple physical terminals must be managed together.

        Parameters
        ----------
        pedb : pyedb.edb.Edb
            EDB object from the ``Edblib`` library, used to access terminal collection
            and convert Python objects to .NET equivalents.
        name : str, optional
            Name to assign to the new bundle terminal. The default is an empty string.
            Individual terminals within the bundle will be renamed to ``{name}:T1``,
            ``{name}:T2``, etc.
        terminals : list, optional
            List of terminals to group into the bundle. Each element can be:

            - A string representing a terminal name (will be looked up in ``pedb.terminals``)
            - A terminal object with a ``.name`` attribute (the object itself or its name
              will be resolved from ``pedb.terminals``)
            - An EDB terminal object (used directly without lookup)

            If ``None``, an empty bundle is created. The default is ``None``.

        Returns
        -------
        BundleTerminal
            The newly created bundle terminal instance.

        Raises
        ------
        ValueError
            If the EDB bundle terminal creation returns a null object, indicating
            a failure to create the bundle with the provided terminals.
        KeyError
            If a terminal name string is provided but cannot be found in
            ``pedb.terminals``.

        Notes
        -----
        The method automatically renames each terminal in the bundle by appending
        a sequence index (`:T1`, `:T2`, etc.) to the base bundle name. This ensures
        unique identification of each terminal within the bundle. If no name is
        provided, terminals are still renamed but without a meaningful prefix.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb("myproject.aedb")
        >>> term1 = edb.terminals["Port1"]
        >>> term2 = edb.terminals["Port2"]
        >>> bundle = BundleTerminal.create(edb, name="DifferentialPair", terminals=[term1, term2])
        >>> if bundle:
        ...     print(f"Bundle created with {len(edb.terminals['DifferentialPair'].terminals)} terminals")

        """
        if isinstance(terminals[0], str):
            terminal_list = [pedb.terminals[i]._edb_object for i in terminals]
        else:
            try:
                terminal_list = [pedb.terminals[i.name]._edb_object for i in terminals]
            except KeyError:
                terminal_list = terminals[::]

        edb_list = convert_py_list_to_net_list(terminal_list, pedb._edb.Cell.Terminal.Terminal)
        _edb_boundle_terminal = pedb._edb.Cell.Terminal.BundleTerminal.Create(edb_list)
        if _edb_boundle_terminal.IsNull():  # pragma no cover
            raise ValueError(f"Failed to create bundle terminal: {name}.")
        _edb_boundle_terminal.SetName(name)
        term_ind = 0
        for term in list(_edb_boundle_terminal.GetTerminals()):
            term_ind += 1
            term.SetName(name + f":T{term_ind}")
        return cls(pedb, _edb_boundle_terminal)
