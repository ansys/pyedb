# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT

"""Resident analytic packets and network palette for RHI mark/cover passes."""

import numpy as np
from PySide6.QtGui import QImage, QRhiBuffer, QRhiTexture

from pyedb.viewer.colors import NET_COLORS


class SdfCoverage:
    def __init__(self):
        self.vbo = self.palette = None
        self.layer_batches = {}
        self.net_ids = {}
        self.component_batches = ()
        self.drawn_pin_count = 0

    def upload(self, device, updates, prepared, *, parent=None):
        previous = self.vbo
        self.vbo = device.buffer(prepared.instances, QRhiBuffer.UsageFlag.VertexBuffer, self.vbo)
        start = len(parent.instances) if parent is not None and previous is self.vbo else 0
        device.upload_buffer(updates, self.vbo, prepared.instances[start:], start * 160)
        if self.palette is None:
            colors = np.full((1, len(NET_COLORS), 4), 255, dtype=np.uint8)
            colors[0, :, :3] = np.rint(np.asarray(NET_COLORS) * 255).astype(np.uint8)
            image = QImage(colors.data, len(NET_COLORS), 1, len(NET_COLORS) * 4, QImage.Format.Format_RGBA8888).copy()
            self.palette = device.create(device.rhi.newTexture(QRhiTexture.Format.RGBA8, image.size()))
            updates.uploadTexture(self.palette, image)
        self.layer_batches = {}
        for batch in prepared.sdf_batches:
            self.layer_batches.setdefault(batch.layer, []).append(batch)
        self.net_ids = {net: index for index, net in enumerate(prepared.nets)}
        self.net_ids[""] = 0
        self.component_batches = prepared.component_batches

    def ranges(self, camera, layers, *, category=None, drills=False):
        ranges = []
        for layer in layers:
            for batch in self.layer_batches.get(layer, ()):
                if category is not None and batch.category != category:
                    continue
                if (drills and not batch.has_drills) or not camera.visible(batch.bounds):
                    continue
                if ranges and sum(ranges[-1]) == batch.instance_start:
                    ranges[-1][1] += batch.instance_count
                else:
                    ranges.append([batch.instance_start, batch.instance_count])
        return ranges
