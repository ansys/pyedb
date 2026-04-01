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

import ast
from pathlib import Path

import pytest

pytestmark = [pytest.mark.integration, pytest.mark.no_licence]


grpc_edb = pytest.importorskip("pyedb.grpc.edb")
dotnet_edb = pytest.importorskip("pyedb.dotnet.edb")


@pytest.mark.parametrize(
    ("backend", "edb_class"),
    [
        ("grpc", grpc_edb.Edb),
        ("dotnet", dotnet_edb.Edb),
    ],
)
def test_edb_deprecated_methods_have_static_metadata(backend, edb_class):
    deprecated_members = {
        "close_edb": "Use close() instead.",
        "save_edb": "Use save() instead.",
        "save_edb_as": "Use save_as() instead.",
    }

    for member_name, expected_message in deprecated_members.items():
        member = getattr(edb_class, member_name)
        assert getattr(member, "__deprecated__", None) == expected_message, (
            f"{backend} Edb.{member_name} should expose static deprecation metadata"
        )


@pytest.mark.parametrize(
    ("backend", "edb_class"),
    [
        ("grpc", grpc_edb.Edb),
        ("dotnet", dotnet_edb.Edb),
    ],
)
def test_edb_deprecated_properties_have_static_metadata(backend, edb_class):
    deprecated_properties = {
        "excitations": "Use ports property instead.",
        "source_excitation": "Use excitation_manager property instead.",
    }

    if backend == "dotnet":
        deprecated_properties["ansys_em_path"] = "Use base_path property instead."

    for property_name, expected_message in deprecated_properties.items():
        property_obj = getattr(edb_class, property_name)
        assert getattr(property_obj.fget, "__deprecated__", None) == expected_message, (
            f"{backend} Edb.{property_name} should expose static deprecation metadata"
        )


def test_top_level_edb_stub_overloads_resolve_to_backend_classes():
    stub_path = Path(__file__).resolve().parents[2] / "src" / "pyedb" / "__init__.pyi"
    stub_tree = ast.parse(stub_path.read_text(encoding="utf-8"))

    imported_aliases = {}
    overloads = []

    for node in stub_tree.body:
        if isinstance(node, ast.ImportFrom):
            module_name = node.module or ""
            if node.level == 1:
                module_name = f"pyedb.{module_name}"
            for alias in node.names:
                imported_aliases[alias.asname or alias.name] = f"{module_name}.{alias.name}"
        elif isinstance(node, ast.FunctionDef) and node.name == "Edb":
            overloads.append(node)

    assert imported_aliases.get("_GrpcEdb") == "pyedb.grpc.edb.Edb"
    assert imported_aliases.get("_DotnetEdb") == "pyedb.dotnet.edb.Edb"
    assert len(overloads) == 3

    expected_signatures = [
        ("Literal[True]", "True", "_GrpcEdb"),
        ("Literal[False]", "False", "_DotnetEdb"),
        ("bool", "False", "_GrpcEdb | _DotnetEdb"),
    ]

    expected_parameter_names = [
        "edbpath",
        "cellname",
        "isreadonly",
        "version",
        "isaedtowned",
        "oproject",
        "student_version",
        "use_ppe",
        "map_file",
        "technology_file",
        "grpc",
        "control_file",
        "layer_filter",
    ]

    for overload_node, (expected_annotation, expected_default, expected_return) in zip(overloads, expected_signatures):
        decorator_names = [
            decorator.id for decorator in overload_node.decorator_list if isinstance(decorator, ast.Name)
        ]
        assert decorator_names == ["overload"]

        parameter_names = [arg.arg for arg in overload_node.args.args]
        assert parameter_names == expected_parameter_names

        grpc_arg = overload_node.args.args[10]
        grpc_default = overload_node.args.defaults[10]
        assert ast.unparse(grpc_arg.annotation) == expected_annotation
        assert ast.unparse(grpc_default) == expected_default
        assert ast.unparse(overload_node.returns) == expected_return
