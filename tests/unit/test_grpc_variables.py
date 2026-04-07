# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT

from unittest.mock import MagicMock
from typing import cast

import pytest

from pyedb.grpc.database.variables import Variable
from pyedb.grpc.edb import Edb as GrpcEdb


class FakeExpression:
    def __init__(self, expression, numeric_value=None):
        self.expression = str(expression)
        self.numeric_value = numeric_value

    def __str__(self):
        return self.expression

    def __float__(self):
        if self.numeric_value is None:
            raise TypeError(f"Expression {self.expression!r} does not have a numeric value.")
        return float(self.numeric_value)

    def _binary(self, operator, other, reverse=False):
        left = other if reverse else self
        right = self if reverse else other
        other_value = float(other)
        if operator == "+":
            numeric_value = float(left) + float(right)
        elif operator == "-":
            numeric_value = float(left) - float(right)
        elif operator == "*":
            numeric_value = float(left) * float(right)
        else:
            numeric_value = float(left) / float(right)
        return FakeExpression(f"({left}){operator}({right})", numeric_value)

    def __add__(self, other):
        return self._binary("+", other)

    def __radd__(self, other):
        return self._binary("+", other, reverse=True)

    def __sub__(self, other):
        return self._binary("-", other)

    def __rsub__(self, other):
        return self._binary("-", other, reverse=True)

    def __mul__(self, other):
        return self._binary("*", other)

    def __rmul__(self, other):
        return self._binary("*", other, reverse=True)

    def __truediv__(self, other):
        return self._binary("/", other)

    def __rtruediv__(self, other):
        return self._binary("/", other, reverse=True)

    def sqrt(self):
        return FakeExpression(f"({self})**0.5", float(self) ** 0.5)


class FakeVariableServer:
    def __init__(self, values, descriptions=None, parameters=None):
        self.values = dict(values)
        self.descriptions = dict(descriptions or {})
        self.parameters = set(parameters or [])

    def get_all_variable_names(self):
        return list(self.values)

    def get_variable_value(self, name):
        return self.values[name]

    def set_variable_value(self, name, value):
        self.values[name] = value

    def get_variable_desc(self, name):
        return self.descriptions.get(name, "")

    def set_variable_desc(self, name, desc):
        self.descriptions[name] = desc

    def is_variable_parameter(self, name):
        return name in self.parameters

    def delete_variable(self, name):
        self.values.pop(name, None)
        self.descriptions.pop(name, None)
        self.parameters.discard(name)
        return True


class FakePedb:
    def __init__(self):
        self.active_cell = FakeVariableServer(
            {"x": 1.0, "y": 2.0},
            descriptions={"x": "x variable"},
            parameters={"x"},
        )
        self.active_db = FakeVariableServer(
            {"$g": 3.0},
            descriptions={"$g": "project variable"},
            parameters={"$g"},
        )

    def value(self, value):
        if isinstance(value, Variable):
            return self.value(value.name)
        if isinstance(value, FakeExpression):
            return value
        if isinstance(value, str):
            if value in self.active_cell.values:
                return FakeExpression(value, self.active_cell.values[value])
            if value in self.active_db.values:
                return FakeExpression(value, self.active_db.values[value])
        return FakeExpression(value, value)


@pytest.mark.unit
def test_grpc_variable_symbolic_arithmetic_uses_variable_names():
    pedb = FakePedb()

    x_obj = Variable(pedb, "x")
    y_obj = Variable(pedb, "y")
    z_obj = x_obj + y_obj + y_obj

    assert str(x_obj) == "x"
    assert float(x_obj) == pytest.approx(1.0)
    assert str(z_obj) == "((x)+(y))+(y)"
    assert float(z_obj) == pytest.approx(5.0)


@pytest.mark.unit
def test_grpc_variable_routes_metadata_and_mutations_to_correct_server():
    pedb = FakePedb()

    design_variable = Variable(pedb, "x")
    project_variable = Variable(pedb, "$g")

    assert design_variable.description == "x variable"
    assert project_variable.description == "project variable"
    assert design_variable.is_parameter is True
    assert project_variable.is_parameter is True

    design_variable.description = "updated design variable"
    project_variable.value = 4.5

    assert pedb.active_cell.descriptions["x"] == "updated design variable"
    assert float(pedb.active_db.values["$g"]) == pytest.approx(4.5)

    assert project_variable.delete() is True
    assert "$g" not in pedb.active_db.get_all_variable_names()


@pytest.mark.unit
def test_grpc_edb_returns_variable_proxies_for_existing_variables():
    edb = GrpcEdb.__new__(GrpcEdb)
    edb._db = FakeVariableServer({"$g": 3.0})
    edb._active_cell = FakeVariableServer({"x": 1.0, "y": 2.0})
    edb.logger = MagicMock()

    design_variable = edb.get_variable("x")
    project_variable = edb.get_variable("$g")
    design_variables = cast(dict[str, Variable], cast(object, edb.design_variables))
    project_variables = cast(dict[str, Variable], cast(object, edb.project_variables))

    assert isinstance(design_variable, Variable)
    assert isinstance(project_variable, Variable)
    assert isinstance(edb.value("x"), Variable)
    assert isinstance(edb.value("$g"), Variable)
    assert design_variable.name == "x"
    assert project_variable.name == "$g"
    assert edb["y"].name == "y"
    assert design_variables["x"]._pedb is edb
    assert project_variables["$g"]._pedb is edb
    assert edb.get_variable("missing") is False

