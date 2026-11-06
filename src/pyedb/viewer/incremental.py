# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT

"""Immutable geometry tails for incremental uploads of live layout edits."""

from bisect import bisect_right
from collections import ChainMap
from dataclasses import replace

import numpy as np


class BufferChain:
    """An immutable sequence of NumPy chunks without copying resident prefixes.

    Normal updates slice only the newly appended tail. A full materialization
    is needed only when a GPU buffer grows or its graphics device is recreated.
    """

    def __init__(self, chunks):
        self.chunks = tuple(chunk for chunk in chunks if len(chunk))
        template = chunks[0]
        self.dtype = template.dtype
        self.shape = (sum(len(chunk) for chunk in self.chunks), *template.shape[1:])
        self.nbytes = sum(chunk.nbytes for chunk in self.chunks)

    def __len__(self):
        return self.shape[0]

    def __array__(self, dtype=None, copy=None):
        data = np.concatenate(self.chunks) if self.chunks else np.empty(self.shape, dtype=self.dtype)
        return np.asarray(data, dtype=dtype)

    def __getitem__(self, key):
        if not isinstance(key, slice) or key.step not in (None, 1):
            return np.asarray(self)[key]
        start, stop, _ = key.indices(len(self))
        chunks = []
        offset = 0
        for chunk in self.chunks:
            end = offset + len(chunk)
            if end > start and offset < stop:
                chunks.append(chunk[max(0, start - offset) : min(len(chunk), stop - offset)])
            offset = end
            if offset >= stop:
                break
        if not chunks:
            return np.empty((0, *self.shape[1:]), dtype=self.dtype)
        return chunks[0] if len(chunks) == 1 else np.concatenate(chunks)

    def tobytes(self):
        return b"".join(chunk.tobytes() for chunk in self.chunks)


def append_buffer(previous, tail):
    """Keep an unchanged buffer identity, or append a small immutable tail."""
    if not len(tail):
        return previous
    chunks = previous.chunks if isinstance(previous, BufferChain) else (previous,)
    return BufferChain((*chunks, tail))


def outline_data(prepared):
    """Use vertex slots for outlines so invalidated geometry need not be moved."""
    if prepared.outlines is not None:
        return prepared.outlines
    edges = np.zeros((len(prepared.vertices), 8), dtype=np.float32)
    for batch in prepared.batches:
        first = batch.vertex_start
        for size in batch.ring_sizes:
            ring = prepared.vertices[first : first + size]
            edges[first : first + size, :4] = ring
            edges[first : first + size, 4:] = np.roll(ring, -1, axis=0)
            first += size
    return edges


def prepare_incremental(scene, previous, parent, patch, changed):
    """Prepare changed objects, retaining all unchanged resident buffer ranges.

    Removed/replaced ranges become unreachable through drawing and picking.
    Periodic compaction bounds tombstones and retained immutable chunks.
    """
    from pyedb.viewer.mesh import prepare_scene, scene_network_names
    from pyedb.viewer.picking import OverlayPickIndex

    if not changed:
        return parent
    affected = sum(item.object_id in changed for item in previous.geometry)
    invalid_sources = {id(item) for item in previous.geometry if item.object_id in changed}
    invalid_ranges = sorted(
        (start, start + count) for source in invalid_sources for start, count in parent.sdf_ranges.get(source, ())
    )
    dead_bytes = (
        parent.dead_bytes
        + sum(
            sum(batch.ring_sizes) * 52 + (batch.outer_count + batch.hole_count) * 4
            for batch in parent.batches
            if batch.object_id in changed
        )
        + sum((end - start) * 168 for start, end in invalid_ranges)
    )
    total_bytes = parent.vertices.nbytes * 13 // 4 + parent.indices.nbytes + parent.instances.nbytes
    # Rebuild occasionally, not once per edit. A single edit on a small scene
    # still follows exactly the same path used by a million-object board.
    if parent.update_count >= 256 or dead_bytes > max(1024 * 1024, total_bytes // 3):
        return prepare_scene(scene)
    nets = tuple(dict.fromkeys((*parent.nets, *scene_network_names(patch))))
    extra = prepare_scene(replace(patch, net_names=nets[1:]))
    if len(parent.vertices) + len(extra.vertices) > np.iinfo(np.uint32).max:
        return prepare_scene(scene)
    vertices = append_buffer(parent.vertices, extra.vertices)
    indices = append_buffer(parent.indices, extra.indices + np.uint32(len(parent.vertices)))
    vertex_nets = append_buffer(parent.vertex_nets, extra.vertex_nets)
    instance_offset = len(parent.instances)
    batches = tuple(batch for batch in parent.batches if batch.object_id not in changed) + tuple(
        replace(
            batch,
            vertex_start=batch.vertex_start + len(parent.vertices),
            index_start=batch.index_start + len(parent.indices),
        )
        for batch in extra.batches
    )
    # Existing SDF chunks may contain several objects. Split their surviving
    # ranges by source identity without regenerating their analytic packets.
    sdf_batches = []
    ends = [end for _, end in invalid_ranges]
    for batch in parent.sdf_batches:
        cursor = batch.instance_start
        stop = cursor + batch.instance_count
        index = bisect_right(ends, cursor)
        if index >= len(invalid_ranges) or invalid_ranges[index][0] >= stop:
            sdf_batches.append(batch)
            continue
        for start, end in invalid_ranges[index:]:
            if start >= stop:
                break
            if start > cursor:
                sdf_batches.append(replace(batch, instance_start=cursor, instance_count=start - cursor))
            cursor = min(stop, max(cursor, end))
        if cursor < stop:
            sdf_batches.append(replace(batch, instance_start=cursor, instance_count=stop - cursor))
    sdf_batches.extend(
        replace(batch, instance_start=batch.instance_start + instance_offset) for batch in extra.sdf_batches
    )
    pin_batches = tuple(batch for batch in parent.pin_batches if batch.pin.object_id not in changed) + tuple(
        replace(
            batch, instance_start=batch.instance_start + instance_offset if batch.instance_start is not None else None
        )
        for batch in extra.pin_batches
    )
    return replace(
        parent,
        vertices=vertices,
        indices=indices,
        batches=batches,
        vertex_nets=vertex_nets,
        instances=append_buffer(parent.instances, extra.instances),
        sdf_batches=tuple(sdf_batches),
        nets=nets,
        pin_batches=pin_batches,
        sdf_sources=append_buffer(parent.sdf_sources, extra.sdf_sources),
        outlines=append_buffer(outline_data(parent), outline_data(extra)),
        mesh_parent_id=id(parent),
        picking=OverlayPickIndex(parent.picking, scene, changed),
        dead_rows=parent.dead_rows + affected,
        dead_bytes=dead_bytes,
        update_count=parent.update_count + 1,
        sdf_ranges=ChainMap(
            {
                key: tuple((start + instance_offset, count) for start, count in ranges)
                for key, ranges in extra.sdf_ranges.items()
            },
            parent.sdf_ranges,
        ),
    )
