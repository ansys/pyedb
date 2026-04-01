from typing import Any, Literal, overload

from pyedb.dotnet.edb import Edb as _DotnetEdb
from pyedb.grpc.edb import Edb as _GrpcEdb
from pyedb import siwave as _siwave


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
    grpc: Literal[True] = True,
    control_file: str | None = None,
    layer_filter: str | None = None,
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
    grpc: Literal[False] = False,
    control_file: str | None = None,
    layer_filter: str | None = None,
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
    grpc: bool = False,
    control_file: str | None = None,
    layer_filter: str | None = None,
) -> _GrpcEdb | _DotnetEdb: ...


def Siwave(specified_version: str | None = None) -> _siwave.Siwave: ...

