# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT

"""Portable RHI resources and frame recording for the layout renderer.

Only Vulkan, Direct3D 11 and Metal are selected. Uniforms use an aligned arena:
each recorded draw owns its values until the frame has been submitted.
"""

import os
from pathlib import Path
import sys

import numpy as np
from PySide6.QtCore import QSize
from PySide6.QtGui import (
    QColor,
    QRhiBuffer,
    QRhiColorAttachment,
    QRhiCommandBuffer,
    QRhiDepthStencilClearValue,
    QRhiGraphicsPipeline,
    QRhiRenderBuffer,
    QRhiSampler,
    QRhiScissor,
    QRhiShaderResourceBinding,
    QRhiShaderStage,
    QRhiTexture,
    QRhiTextureRenderTarget,
    QRhiTextureRenderTargetDescription,
    QRhiVertexInputAttribute,
    QRhiVertexInputBinding,
    QRhiVertexInputLayout,
    QRhiViewport,
    QShader,
)
from PySide6.QtWidgets import QRhiWidget
from PySide6.support import VoidPtr

from pyedb.viewer.mesh import split_coordinates

UNIFORM_SIZE = 256


def allocate_geometry_buffer(rhi, usage, size):
    """Allocate geometry separately from the per-frame uniform arena."""
    return rhi.newBuffer(QRhiBuffer.Type.Static, usage, size)


def upload_geometry_buffer(updates, buffer, offset, data):
    """Upload resident bytes; navigation never calls this function."""
    # Qt 6.8 exposes the size/pointer overload, but not the bytes convenience
    # overload. QRhi copies the data into the update batch before returning.
    try:
        updates.uploadStaticBuffer(buffer, offset, data)
    except TypeError:
        updates.uploadStaticBuffer(buffer, offset, len(data), VoidPtr(data))


def graphics_api(backend=None, platform=None):
    """Resolve an explicit, platform-compatible backend without a graphics device."""
    platform = sys.platform if platform is None else platform
    name = backend or os.environ.get("PYEDB_VIEWER_BACKEND", "auto")
    name = name.lower()
    if name == "auto":
        name = "d3d11" if platform == "win32" else "metal" if platform == "darwin" else "vulkan"
    apis = {"vulkan": QRhiWidget.Api.Vulkan, "d3d11": QRhiWidget.Api.Direct3D11, "metal": QRhiWidget.Api.Metal}
    if name not in apis:
        raise ValueError("Layout backend must be 'auto', 'vulkan', 'd3d11' or 'metal'.")
    if name == "d3d11" and platform != "win32":
        raise ValueError("The d3d11 layout backend requires Windows.")
    if name == "metal" and platform != "darwin":
        raise ValueError("The metal layout backend requires macOS.")
    return name, apis[name]


def camera_uniforms(rhi, camera, pixel_ratio):
    """Pack the shared std140 block, retaining high/low camera coordinates."""
    values = np.zeros(UNIFORM_SIZE // 4, dtype=np.float32)
    values[:16] = rhi.clipSpaceCorrMatrix().data()
    values[16:20] = split_coordinates([[camera.center_x, camera.center_y]])[0]
    values[20:24] = camera.width, camera.height, camera.scale, pixel_ratio
    values[24:28] = -1 if camera.mirror else 1, -1, 0, 0
    values[28:32] = 1
    values[56:60] = 1, float(rhi.isYUpInFramebuffer()), 0, 0
    return values


class Target:
    """A reusable color/resolve target with optional object-local stencil."""

    def __init__(self, device, size, samples=1, *, description=None, preserve=False):
        self.device = device
        self.resources = []
        self.size = QSize(size)
        self.samples = samples
        if description is None:
            self.texture = self._create(
                device.rhi.newTexture(QRhiTexture.Format.RGBA8, size, 1, QRhiTexture.Flag.RenderTarget)
            )
            attachment = QRhiColorAttachment(self.texture)
            if samples > 1:
                color = self._create(device.rhi.newRenderBuffer(QRhiRenderBuffer.Type.Color, size, samples))
                attachment = QRhiColorAttachment(color)
                attachment.setResolveTexture(self.texture)
            stencil = self._create(device.rhi.newRenderBuffer(QRhiRenderBuffer.Type.DepthStencil, size, samples))
            description = QRhiTextureRenderTargetDescription(attachment, stencil)
        else:
            self.texture = None  # All attachments belong to QRhiWidget.
        flags = QRhiTextureRenderTarget.Flag.PreserveColorContents if preserve else QRhiTextureRenderTarget.Flag(0)
        self.target = device.rhi.newTextureRenderTarget(description, flags)
        self.resources.append(self.target)
        self.descriptor = self.target.newCompatibleRenderPassDescriptor()
        self.resources.append(self.descriptor)
        self.resources[-2:] = [self.descriptor, self.target]
        self.target.setRenderPassDescriptor(self.descriptor)
        if not self.target.create():
            self.release()
            raise RuntimeError("Could not create the layout render target.")

    def _create(self, resource):
        self.resources.append(resource)
        if not resource.create():
            self.release()
            raise RuntimeError("Could not allocate the layout render attachments.")
        return resource

    def release(self):
        for resource in reversed(self.resources):
            resource.destroy()
        self.resources.clear()


class Device:
    """Own pipelines, resident buffers and an aligned per-frame uniform arena."""

    def __init__(self, rhi):
        self.rhi = rhi
        self.resources = []
        self.pipelines = {}
        self.bindings = {}
        self.shaders = {}
        self.uniform_buffer = None
        self.uniform_capacity = 0
        self.stride = rhi.ubufAligned(UNIFORM_SIZE)
        self.passes = []
        self.uniforms = []
        self.current = None
        self.geometry_upload_bytes = 0
        self.sampler = self.create(
            rhi.newSampler(
                QRhiSampler.Filter.Linear,
                QRhiSampler.Filter.Linear,
                QRhiSampler.Filter.None_,
                QRhiSampler.AddressMode.ClampToEdge,
                QRhiSampler.AddressMode.ClampToEdge,
            )
        )

    def create(self, resource):
        self.resources.append(resource)
        if not resource.create():
            raise RuntimeError("Could not create a layout GPU resource.")
        return resource

    def buffer(self, data, usage, previous=None):
        """Allocate a resident buffer, retaining append capacity between snapshots."""
        size = data.nbytes
        if previous is None or previous.size() < max(4, size):
            if previous is not None:
                previous.deleteLater()
                self.resources.remove(previous)
            previous = self.create(allocate_geometry_buffer(self.rhi, usage, max(4, size + 65536)))
        return previous

    def upload_buffer(self, updates, buffer, data, offset=0):
        if data.nbytes:
            upload_geometry_buffer(updates, buffer, offset, data.tobytes())
            self.geometry_upload_bytes += data.nbytes

    def shader(self, name):
        if name not in self.shaders:
            path = Path(__file__).with_name("shaders") / f"{name}.qsb"
            if not path.is_file():
                raise RuntimeError(
                    "Layout shader packs are missing. Install a built wheel or run "
                    "'python tools/bake_viewer_shaders.py' from the source checkout."
                )
            shader = QShader.fromSerialized(path.read_bytes())
            if not shader.isValid():
                raise RuntimeError(f"Invalid layout shader: {path.name}")
            self.shaders[name] = shader
        return self.shaders[name]

    def begin_frame(self):
        self.passes = []
        self.uniforms = []
        self.current = None

    def begin_pass(self, target, clear=(0, 0, 0, 0)):
        self.current = []
        self.passes.append((target, clear, self.current))

    def draw(
        self,
        shader,
        uniforms,
        *,
        layout="quad",
        buffers=(),
        index=None,
        start=0,
        count=4,
        instances=1,
        texture=None,
        blend="alpha",
        stencil=None,
        scissor=None,
        reference=0,
    ):
        self.current.append(
            (
                shader,
                layout,
                buffers,
                index,
                start,
                count,
                instances,
                texture,
                blend,
                stencil,
                scissor,
                reference,
                len(self.uniforms),
            )
        )
        self.uniforms.append(uniforms.copy())

    def _binding(self, texture):
        key = id(texture)
        if key not in self.bindings:
            stage = QRhiShaderResourceBinding.StageFlag
            bindings = [
                QRhiShaderResourceBinding.uniformBufferWithDynamicOffset(
                    0, stage.VertexStage | stage.FragmentStage, self.uniform_buffer, UNIFORM_SIZE
                )
            ]
            if texture is not None:
                bindings.append(QRhiShaderResourceBinding.sampledTexture(1, stage.FragmentStage, texture, self.sampler))
            srb = self.rhi.newShaderResourceBindings()
            srb.setBindings(bindings)
            self.bindings[key] = self.create(srb)
        return self.bindings[key]

    def _pipeline(self, target, shader, layout, texture, blend, stencil, scissor):
        key = id(target.descriptor), shader, layout, texture is not None, blend, stencil, scissor is not None
        if key in self.pipelines:
            return self.pipelines[key]
        pipeline = self.rhi.newGraphicsPipeline()
        self.resources.append(pipeline)
        vertex = (
            ("copper.vert" if layout == "mesh" else "rectangle.vert")
            if shader == "copper"
            else "sdf.vert"
            if shader == "sdf"
            else ("label.vert" if shader == "label" else "outline.vert" if shader == "outline" else "coverage.vert")
        )
        pipeline.setShaderStages(
            [
                QRhiShaderStage(QRhiShaderStage.Type.Vertex, self.shader(vertex)),
                QRhiShaderStage(QRhiShaderStage.Type.Fragment, self.shader(f"{shader}.frag")),
            ]
        )
        pipeline.setTopology(
            QRhiGraphicsPipeline.Topology.Triangles
            if layout in ("mesh", "fullscreen")
            else QRhiGraphicsPipeline.Topology.TriangleStrip
        )
        inputs = QRhiVertexInputLayout()
        if layout == "mesh":
            inputs.setBindings([QRhiVertexInputBinding(16), QRhiVertexInputBinding(4)])
            inputs.setAttributes(
                [
                    QRhiVertexInputAttribute(0, 0, QRhiVertexInputAttribute.Format.Float4, 0),
                    QRhiVertexInputAttribute(1, 1, QRhiVertexInputAttribute.Format.UInt, 0),
                ]
            )
        elif layout == "outline":
            inputs.setBindings(
                [
                    QRhiVertexInputBinding(32, QRhiVertexInputBinding.Classification.PerInstance),
                    QRhiVertexInputBinding(4, QRhiVertexInputBinding.Classification.PerInstance),
                ]
            )
            inputs.setAttributes(
                [
                    QRhiVertexInputAttribute(0, 0, QRhiVertexInputAttribute.Format.Float4, 0),
                    QRhiVertexInputAttribute(0, 1, QRhiVertexInputAttribute.Format.Float4, 16),
                    QRhiVertexInputAttribute(1, 2, QRhiVertexInputAttribute.Format.UInt, 0),
                ]
            )
        elif layout in ("sdf", "label"):
            fields = {"sdf": 10, "label": 3}[layout]
            inputs.setBindings([QRhiVertexInputBinding(fields * 16, QRhiVertexInputBinding.Classification.PerInstance)])
            inputs.setAttributes(
                [QRhiVertexInputAttribute(0, i, QRhiVertexInputAttribute.Format.Float4, i * 16) for i in range(fields)]
            )
        pipeline.setVertexInputLayout(inputs)
        pipeline.setSampleCount(target.samples)
        state = QRhiGraphicsPipeline.TargetBlend()
        if blend == "none":
            state.colorWrite = QRhiGraphicsPipeline.ColorMaskComponent(0)
        elif blend in ("alpha", "union"):
            state.enable = True
            state.srcColor = (
                QRhiGraphicsPipeline.BlendFactor.SrcAlpha
                if blend == "alpha"
                else (QRhiGraphicsPipeline.BlendFactor.One)
            )
            state.dstColor = (
                QRhiGraphicsPipeline.BlendFactor.OneMinusSrcAlpha
                if blend == "alpha"
                else (QRhiGraphicsPipeline.BlendFactor.Zero)
            )
            state.srcAlpha = QRhiGraphicsPipeline.BlendFactor.One
            state.dstAlpha = (
                QRhiGraphicsPipeline.BlendFactor.OneMinusSrcAlpha
                if blend == "alpha"
                else (QRhiGraphicsPipeline.BlendFactor.One)
            )
            if blend == "union":
                state.opAlpha = QRhiGraphicsPipeline.BlendOp.Max
        pipeline.setTargetBlends([state])
        flags = QRhiGraphicsPipeline.Flag(0)
        if stencil is not None:
            operation, write_mask = stencil
            flags |= QRhiGraphicsPipeline.Flag.UsesStencilRef
            pipeline.setStencilTest(True)
            pipeline.setStencilReadMask(3)
            pipeline.setStencilWriteMask(write_mask)
            state = QRhiGraphicsPipeline.StencilOpState()
            state.compareOp = (
                QRhiGraphicsPipeline.CompareOp.Equal
                if operation == "cover"
                else (QRhiGraphicsPipeline.CompareOp.Always)
            )
            state.passOp = (
                QRhiGraphicsPipeline.StencilOp.Replace
                if operation == "mark"
                else (
                    QRhiGraphicsPipeline.StencilOp.StencilZero
                    if operation == "clear"
                    else QRhiGraphicsPipeline.StencilOp.Keep
                )
            )
            pipeline.setStencilFront(state)
            pipeline.setStencilBack(state)
        if scissor is not None:
            flags |= QRhiGraphicsPipeline.Flag.UsesScissor
        pipeline.setFlags(flags)
        pipeline.setShaderResourceBindings(self._binding(texture))
        pipeline.setRenderPassDescriptor(target.descriptor)
        if not pipeline.create():
            raise RuntimeError(f"Could not create layout pipeline: {shader}/{layout}.")
        self.pipelines[key] = pipeline
        return pipeline

    def submit(self, command_buffer, updates):
        """Upload each draw's constants once, then execute the recorded passes."""
        required = max(1, len(self.uniforms)) * self.stride
        if required > self.uniform_capacity:
            # Pipelines retain their layout SRB. Rebuild both before replacing
            # the arena so no pipeline refers to a retired binding object.
            self.release_targets()
            if self.uniform_buffer is not None:
                self.uniform_buffer.deleteLater()
                self.resources.remove(self.uniform_buffer)
            self.uniform_capacity = max(required, self.uniform_capacity * 2, 65536)
            self.uniform_buffer = self.create(
                self.rhi.newBuffer(QRhiBuffer.Type.Dynamic, QRhiBuffer.UsageFlag.UniformBuffer, self.uniform_capacity)
            )
        data = bytearray(required)
        for index, values in enumerate(self.uniforms):
            data[index * self.stride : index * self.stride + UNIFORM_SIZE] = values.tobytes()
        try:
            updates.updateDynamicBuffer(self.uniform_buffer, 0, data)
        except TypeError:
            updates.updateDynamicBuffer(self.uniform_buffer, 0, len(data), VoidPtr(data))
        command_buffer.resourceUpdate(updates)
        for target, clear, commands in self.passes:
            command_buffer.beginPass(target.target, QColor.fromRgbF(*clear), QRhiDepthStencilClearValue(1, 0))
            try:
                for (
                    shader,
                    layout,
                    buffers,
                    index,
                    start,
                    count,
                    instances,
                    texture,
                    blend,
                    stencil,
                    scissor,
                    reference,
                    uniform_index,
                ) in commands:
                    pipeline = self._pipeline(target, shader, layout, texture, blend, stencil, scissor)
                    command_buffer.setGraphicsPipeline(pipeline)
                    # Vulkan always scissors. QRhi derives the full scissor from
                    # the *active* pipeline when setting its viewport.
                    command_buffer.setViewport(QRhiViewport(0, 0, target.size.width(), target.size.height()))
                    command_buffer.setShaderResources(self._binding(texture), 1, (0, uniform_index * self.stride))
                    if stencil is not None:
                        command_buffer.setStencilRef(reference)
                    if scissor is not None:
                        command_buffer.setScissor(QRhiScissor(*scissor))
                    if buffers:
                        if index is None:
                            command_buffer.setVertexInput(0, list(buffers))
                        else:
                            command_buffer.setVertexInput(
                                0, list(buffers), index, 0, QRhiCommandBuffer.IndexFormat.IndexUInt32
                            )
                    if index is None:
                        command_buffer.draw(count, instances, start)
                    else:
                        command_buffer.drawIndexed(count, instances, start)
            finally:
                command_buffer.endPass()

    def release_targets(self):
        """Drop pipelines/bindings before their attachments are resized or destroyed."""
        for resource in (*self.pipelines.values(), *self.bindings.values()):
            resource.deleteLater()
            self.resources.remove(resource)
        self.pipelines.clear()
        self.bindings.clear()

    def release(self):
        for resource in reversed(self.resources):
            resource.destroy()
        self.resources.clear()
        self.pipelines.clear()
        self.bindings.clear()
