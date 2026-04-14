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

from typing import Any, Literal, overload

from .dotnet.edb import Edb as _DotnetEdb
from .grpc.edb import Edb as _GrpcEdb
from .siwave import Siwave

@overload
def Edb(
    edbpath: str | None = None,
    cellname: str | None = None,
    isreadonly: bool = False,
    version: str | None = None,
    isaedtowned: bool = False,
    oproject: Any = None,
    student_version: bool = False,
    use_ppe: bool = False,
    map_file: str | None = None,
    technology_file: str | None = None,
    grpc: Literal[True] = ...,
    control_file: str | None = None,
    layer_filter: str | None = None,
    in_memory: bool = True,
) -> _GrpcEdb: ...
@overload
def Edb(
    edbpath: str | None = None,
    cellname: str | None = None,
    isreadonly: bool = False,
    version: str | None = None,
    isaedtowned: bool = False,
    oproject: Any = None,
    student_version: bool = False,
    use_ppe: bool = False,
    map_file: str | None = None,
    technology_file: str | None = None,
    grpc: Literal[False] = ...,
    control_file: str | None = None,
    layer_filter: str | None = None,
    in_memory: bool = True,
) -> _DotnetEdb: ...
@overload
def Edb(
    edbpath: str | None = None,
    cellname: str | None = None,
    isreadonly: bool = False,
    version: str | None = None,
    isaedtowned: bool = False,
    oproject: Any = None,
    student_version: bool = False,
    use_ppe: bool = False,
    map_file: str | None = None,
    technology_file: str | None = None,
    grpc: bool = ...,
    control_file: str | None = None,
    layer_filter: str | None = None,
    in_memory: bool = True,
) -> _GrpcEdb | _DotnetEdb: ...
@overload
def Edb(
    edbpath: str | None = None,
    cellname: str | None = None,
    isreadonly: bool = False,
    version: str | None = None,
    isaedtowned: bool = False,
    oproject: Any = None,
    student_version: bool = False,
    use_ppe: bool = False,
    map_file: str | None = None,
    technology_file: str | None = None,
    grpc: None = None,
    control_file: str | None = None,
    layer_filter: str | None = None,
    in_memory: bool = True,
) -> _GrpcEdb | _DotnetEdb: ...

pyedb_path: str
__version__: str
version: str
