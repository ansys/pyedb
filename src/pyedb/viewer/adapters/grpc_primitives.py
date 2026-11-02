# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT

"""Enumerate all primitives with the SDK factory and viewer-relevant prefetch."""

import sys

from ansys.api.edb.v1.layout_obj_pb2 import LayoutObjTargetMessage
from ansys.edb.core import session as core_session
from ansys.edb.core.edb_defs import LayoutObjType
from ansys.edb.core.inner.factory import create_lyt_obj
from ansys.edb.core.layout.layout import Layout as CoreLayout
from ansys.edb.core.session import StubAccessor, StubType
from ansys.edb.core.utility.io_manager import get_cache

# Do not whitelist geometry: retain unknown/new prefetched responses and every
# shape-specific property, including analytic trace and parameter data.
_UNUSED_PREFETCH = {
    "ansys.api.edb.v1.ConnectableService": {"GetObjType", "GetComponent", "GetGroup"},
    "ansys.api.edb.v1.LayoutObjService": {"GetLayout"},
    "ansys.api.edb.v1.PrimitiveService": {"GetOwner", "IsParameterized", "IsZonePrimitive", "GetHfssProp"},
}


def _discard_unused_prefetch(message):
    """Skip only known properties never consumed by a detached viewer capture."""
    entries = message.cache.cache
    removed = 0
    for index in range(len(entries) - 1, -1, -1):
        entry = entries[index]
        if entry.rpc_method_name in _UNUSED_PREFETCH.get(entry.service_name, ()):
            del entries[index]
            removed += 1
    return removed


class PrimitiveReader:
    """Use the same StreamItems RPC, omitting unused client-side Any decoding.

    No server-side filter or reduced wire payload is implied. Writable,
    cache-disabled and shared-memory sessions retain the SDK's normal reader.
    """

    def __init__(self, edb):
        self.edb = edb
        self.discarded = 0

    def read(self):
        layout = self.edb.layout
        core = getattr(layout, "core", None)
        session = core_session.MOD.current_session
        if (
            not getattr(self.edb, "isreadonly", False)
            or not isinstance(core, CoreLayout)
            or get_cache() is None
            or session is None
            or getattr(session, "shared_memory", False)
        ):
            return layout.primitives
        request = LayoutObjTargetMessage(target=core.msg, type=LayoutObjType.PRIMITIVE.value)
        stream = StubAccessor(StubType.layout).__get__().StreamItems(request)
        result = []
        try:
            for batch in stream:
                for message in batch.items:
                    self.discarded += _discard_unused_prefetch(message)
                    primitive = layout._wrap_primitive(create_lyt_obj(message, LayoutObjType.PRIMITIVE))
                    if primitive is not None:
                        result.append(primitive)
        finally:
            # Older EDB servers require streams to finish before database close.
            failing = sys.exc_info()[0] is not None
            try:
                for _ in stream:
                    pass
            except Exception:
                if not failing:
                    raise
        return result
