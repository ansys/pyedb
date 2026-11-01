# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT

"""Bounded read-only getter prefetch, isolated from the SDK's mutable interceptors."""

from itertools import islice

from ansys.api.edb.v1.edb_messages_pb2 import EDBObjMessage
from ansys.api.edb.v1.padstack_instance_pb2_grpc import PadstackInstanceServiceStub
from ansys.edb.core import session as core_session
from ansys.edb.core.primitive.padstack_instance import PadstackInstance as CorePadstackInstance
from ansys.edb.core.utility.io_manager import get_cache
import grpc


class PadInstances:
    """Feed standard SDK getters from exact, asynchronously fetched responses.

    Only raw protobufs cross the extra channel. Cache insertion and all model
    construction stay on the single capture worker, without sharing the SDK's
    stateful IOInterceptor between concurrent calls.
    """

    def __init__(self, edb, instances, window=16, *, fetched=None):
        self.edb, self.instances, self.window = edb, instances, window
        self.fetched = set() if fetched is None else fetched
        self.prefetched = 0
        self.disabled = False

    def __len__(self):
        return len(self.instances)

    def _open(self):
        session = core_session.MOD.current_session
        if (
            not getattr(self.edb, "isreadonly", False)
            or session is None
            or get_cache() is None
            or getattr(session, "shared_memory", False)
            or getattr(session, "ip_address", None) != "localhost"
        ):
            return None
        mode = getattr(session, "transport_mode", None)
        if mode == "uds":
            parameters = {"transport_mode": mode, "uds_fullpath": session._get_uds_file()}
        elif mode in {"wnua", "insecure"}:
            parameters = {"transport_mode": mode, "host": session.ip_address, "port": session.port_num}
        else:
            return None
        return core_session.create_channel(**parameters)

    def __iter__(self):
        source = iter(self.instances)
        first = list(islice(source, self.window))
        if not first:
            return
        if not all(isinstance(getattr(item, "core", None), CorePadstackInstance) for item in first):
            yield from first
            yield from source
            return
        channel = None
        try:
            try:
                channel = self._open()
            except (AttributeError, OSError, RuntimeError):
                self.disabled = True
            if channel is None:
                yield from first
                yield from source
                return
            stub = PadstackInstanceServiceStub(channel)
            batch = first
            while batch:
                if not self.disabled:
                    self._prefetch(stub, batch)
                yield from batch
                batch = list(islice(source, self.window))
        finally:
            if channel is not None:
                channel.close()

    def _prefetch(self, stub, batch):
        batch = [item for item in batch if item.core.id not in self.fetched]
        pending = []
        try:
            for item in batch:
                request = EDBObjMessage(id=item.core.id)
                mapping = stub.GetLayerMap.future(request, timeout=10)
                pending.append((request, "GetLayerMap", mapping))
                override = stub.GetHoleOverrides.future(request, timeout=10)
                pending.append((request, "GetHoleOverrides", override))
            responses = [(request, method, future.result()) for request, method, future in pending]
        except Exception as error:
            # Complete every submitted read before closing its channel or the
            # caller-owned database. Unsupported servers retain the old path.
            for _, _, future in pending:
                try:
                    future.result()
                except Exception:
                    pass
            self.disabled = True
            if isinstance(error, grpc.RpcError) and error.code() in {
                grpc.StatusCode.UNAVAILABLE,
                grpc.StatusCode.DEADLINE_EXCEEDED,
            }:
                raise
            return
        cache = get_cache()
        if cache is not None:
            for request, method, response in responses:
                cache.add("ansys.api.edb.v1.PadstackInstanceService", method, request, response)
            self.prefetched += len(batch)
            self.fetched.update(item.core.id for item in batch)
