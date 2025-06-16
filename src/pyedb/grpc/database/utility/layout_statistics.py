# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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


class LayoutStatistics(object):
    """Statistics object

    Object properties example.
    >>> stat_model = EDBStatistics()
    >>> stat_model.num_capacitors
    >>> stat_model.num_resistors
    >>> stat_model.num_inductors
    >>> stat_model.layout_size
    >>> stat_model.num_discrete_components
    >>> stat_model.num_inductors
    >>> stat_model.num_resistors
    >>> stat_model.num_capacitors
    >>> stat_model.num_nets
    >>> stat_model.num_traces
    >>> stat_model.num_polygons
    >>> stat_model.num_vias
    >>> stat_model.stackup_thickness
    >>> stat_model.occupying_surface
    >>> stat_model.occupying_ratio
    """

    def __init__(self):
        self._nb_layer = 0
        self._stackup_thickness = 0.0
        self._nb_vias = 0
        self._occupying_ratio = {}
        self._occupying_surface = {}
        self._layout_size = [0.0, 0.0, 0.0, 0.0]
        self._nb_polygons = 0
        self._nb_traces = 0
        self._nb_nets = 0
        self._nb_discrete_components = 0
        self._nb_inductors = 0
        self._nb_capacitors = 0
        self._nb_resistors = 0

    @property
    def num_layers(self) -> int:
        """Layer number.

        Returns
        -------
        int
            Number of layers.

        """
        return self._nb_layer

    @num_layers.setter
    def num_layers(self, value):
        if isinstance(value, int):
            self._nb_layer = value

    @property
    def stackup_thickness(self) -> float:
        """Stackup total thickness.

        Returns
        -------
        float
            Stack up total thickness value.

        """

        return self._stackup_thickness

    @stackup_thickness.setter
    def stackup_thickness(self, value):
        if isinstance(value, float):
            self._stackup_thickness = value

    @property
    def num_vias(self) -> int:
        """Via number.

        Returns
        -------
        int
            Total number of vias.

        """
        return self._nb_vias

    @num_vias.setter
    def num_vias(self, value):
        if isinstance(value, int):
            self._nb_vias = value

    @property
    def occupying_ratio(self) -> float:
        """Occupying ratio.

        Returns
        -------
        float
            Occupying ration value.
            Value representing metal coverage versus total layout surface.

        """
        return self._occupying_ratio

    @occupying_ratio.setter
    def occupying_ratio(self, value):
        if isinstance(value, float):
            self._occupying_ratio = value

    @property
    def occupying_surface(self) -> bool:
        """Occupying surface.

        Returns
        -------
        float
            Occupying surface value.

        """
        return self._occupying_surface

    @occupying_surface.setter
    def occupying_surface(self, value):
        if isinstance(value, float):
            self._occupying_surface = value

    @property
    def layout_size(self) -> list[float]:
        """Layout size.

        Returns
        -------
        List[(float, float), (float, float)]
            Layout bounding box, lower left corner (x, y) upper right corner (x, y).

        """
        return self._layout_size

    @property
    def num_polygons(self) -> int:
        """Polygon number.

        Returns
        -------
        int
            Total number of polygons.

        """
        return self._nb_polygons

    @num_polygons.setter
    def num_polygons(self, value):
        if isinstance(value, int):
            self._nb_polygons = value

    @property
    def num_traces(self) -> int:
        """Trace number.

        Returns
        -------
        int
            Total number of traces.

        """
        return self._nb_traces

    @num_traces.setter
    def num_traces(self, value):
        if isinstance(value, int):
            self._nb_traces = value

    @property
    def num_nets(self) -> int:
        """Net number.

        Returns
        -------
        int
            Total number og nets.

        """
        return self._nb_nets

    @num_nets.setter
    def num_nets(self, value):
        if isinstance(value, int):
            self._nb_nets = value

    @property
    def num_discrete_components(self) -> int:
        """Discrete component number.

        Returns
        -------
        int
            Total number of discrete components.

        """
        return self._nb_discrete_components

    @num_discrete_components.setter
    def num_discrete_components(self, value):
        if isinstance(value, int):
            self._nb_discrete_components = value

    @property
    def num_inductors(self) -> int:
        """Inductor number.

        Returns
        -------
        int
            Total number of inductors.

        """
        return self._nb_inductors

    @num_inductors.setter
    def num_inductors(self, value):
        if isinstance(value, int):
            self._nb_inductors = value

    @property
    def num_capacitors(self) -> int:
        """Capacitor number.

        Returns
        -------
        int
            Total number of capacitors.

        """
        return self._nb_capacitors

    @num_capacitors.setter
    def num_capacitors(self, value):
        if isinstance(value, int):
            self._nb_capacitors = value

    @property
    def num_resistors(self) -> int:
        """Resistor number.

        Returns
        -------
        int
            Total number of resistors.

        """
        return self._nb_resistors

    @num_resistors.setter
    def num_resistors(self, value):
        if isinstance(value, int):
            self._nb_resistors = value
