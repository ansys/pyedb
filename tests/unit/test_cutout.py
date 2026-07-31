# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

"""Unit tests for GrpcCutout.run() – no EDB licence required."""

from types import SimpleNamespace
from unittest.mock import MagicMock, call, patch

import pytest

from pyedb.workflows.utilities.cutout import GrpcCutout


def _make_edb(edbpath="/original/design.aedb"):
    """Return a lightweight mock that mimics the gRPC Edb object."""
    edb = MagicMock()
    edb.edbpath = edbpath
    edb.value = lambda v: float(v) if not isinstance(v, str) else 0.002

    # save_as updates edbpath to the target path, just like the real implementation.
    def _save_as(path, *args, **kwargs):
        edb.edbpath = path
        return True

    edb.save_as.side_effect = _save_as
    return edb


@pytest.mark.unit
@pytest.mark.grpc
class TestGrpcCutoutRun:
    """Tests for GrpcCutout.run() focusing on the open_cutout_at_end=False branch."""

    def _make_cutout(self, edb, output_file="/output/cutout.aedb"):
        """Build a GrpcCutout with minimal required attributes."""
        cutout = GrpcCutout.__new__(GrpcCutout)
        cutout._edb = edb
        cutout.signals = ["NET_A"]
        cutout.references = ["NET_B"]
        cutout.extent_type = "ConvexHull"
        cutout.expansion_size = 0.002
        cutout.use_round_corner = False
        cutout.output_file = output_file
        cutout.open_cutout_at_end = False
        cutout.use_pyaedt_cutout = True
        cutout.smart_cutout = False
        cutout.number_of_threads = 1
        cutout.use_pyaedt_extent_computing = True
        cutout.extent_defeature = 0
        cutout.remove_single_pin_components = False
        cutout.custom_extent = None
        cutout.custom_extent_units = "mm"
        cutout.include_partial_instances = False
        cutout.keep_voids = True
        cutout.check_terminals = False
        cutout.include_pingroups = False
        cutout.expansion_factor = 0
        cutout.maximum_iterations = 10
        cutout.preserve_components_with_model = False
        cutout.simple_pad_check = True
        cutout.keep_lines_as_path = False
        cutout.include_voids_in_extents = False
        cutout.compute_extent_only = False
        return cutout

    def test_open_cutout_at_end_false_calls_close_without_terminating_rpc(self):
        """When open_cutout_at_end=False and output_file is set, close() must be
        called with terminate_rpc_session=False so the RPC server is kept alive
        for the subsequent open() call that restores the original EDB.

        Regression: PyEDB 0.81.0 called the non-existent open_edb() method here,
        raising AttributeError. The fix uses open() and preserves the RPC session.
        """
        original_path = "/original/design.aedb"
        output_path = "/output/cutout.aedb"
        fake_extent = [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]]

        edb = _make_edb(original_path)
        cutout = self._make_cutout(edb, output_file=output_path)

        with patch.object(cutout, "_create_cutout_multithread", return_value=fake_extent) as mock_cut:
            result = cutout.run()

        # Cutout should succeed and return the extent polygon.
        assert result == fake_extent

        # save_as must be called with the output path.
        edb.save_as.assert_called_with(output_path)

        # close() must be called with terminate_rpc_session=False (not with default args
        # which would shut the RPC server down before the subsequent open() call).
        edb.close.assert_called_once_with(terminate_rpc_session=False)

        # After close(), edbpath must be restored to the original before open().
        # We verify open() was called (re-opening the original EDB).
        edb.open.assert_called_once()

    def test_open_cutout_at_end_false_no_output_file_does_not_reopen(self):
        """When open_cutout_at_end=False but no output_file is given, the cutout is
        saved in-place to legacy_path.  The edbpath does not change after save_as,
        so no close/reopen cycle is needed.
        """
        original_path = "/original/design.aedb"
        fake_extent = [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]]

        edb = _make_edb(original_path)
        cutout = self._make_cutout(edb, output_file="")

        with patch.object(cutout, "_create_cutout_multithread", return_value=fake_extent):
            result = cutout.run()

        assert result == fake_extent
        # In-place save: legacy_path is used.
        edb.save_as.assert_called_once_with(original_path)
        # edbpath stays at legacy_path after save → no close/reopen needed.
        edb.close.assert_not_called()
        edb.open.assert_not_called()

    def test_open_cutout_at_end_true_does_not_close(self):
        """When open_cutout_at_end=True (default), the cutout EDB remains open and
        the original is NOT reopened.
        """
        original_path = "/original/design.aedb"
        output_path = "/output/cutout.aedb"
        fake_extent = [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]]

        edb = _make_edb(original_path)
        cutout = self._make_cutout(edb, output_file=output_path)
        cutout.open_cutout_at_end = True

        with patch.object(cutout, "_create_cutout_multithread", return_value=fake_extent):
            result = cutout.run()

        assert result == fake_extent
        edb.close.assert_not_called()
        edb.open.assert_not_called()

    def test_retry_loop_uses_terminate_rpc_session_false(self):
        """On a failed attempt the retry loop must restore the original EDB using
        close(terminate_rpc_session=False), not close() with default arguments.
        """
        original_path = "/original/design.aedb"
        output_path = "/output/cutout.aedb"
        fake_extent = [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]]

        edb = _make_edb(original_path)
        cutout = self._make_cutout(edb, output_file=output_path)
        # Enable smart cutout so the retry loop can run more than once.
        cutout.smart_cutout = True
        cutout.maximum_iterations = 2
        cutout.open_cutout_at_end = True  # Don't trigger the restoration branch.

        # First attempt fails, second succeeds.
        with patch.object(cutout, "_create_cutout_multithread", side_effect=[[], fake_extent]):
            with patch.object(cutout, "are_port_reference_terminals_connected", return_value=True, create=True):
                # are_port_reference_terminals_connected lives on _edb, not cutout.
                edb.are_port_reference_terminals_connected.return_value = True
                result = cutout.run()

        # The retry close() call must preserve the RPC session.
        edb.close.assert_called_once_with(terminate_rpc_session=False)

    def test_grpc_cutout_does_not_save_inside_create_cutout_multithread(self):
        """_create_cutout_multithread must not call save_as internally.
        The save is the exclusive responsibility of run().  This prevents partial
        cutout data from being written to output_file on a failed attempt.
        """
        original_path = "/original/design.aedb"
        output_path = "/output/cutout.aedb"

        edb = _make_edb(original_path)
        cutout = self._make_cutout(edb, output_file=output_path)

        # Run the real _create_cutout_multithread with all heavy methods mocked out.
        cutout._extent = MagicMock(
            return_value=MagicMock(
                points=[[0, 0], [1, 0], [1, 1]],
                without_arcs=MagicMock(
                    return_value=MagicMock(
                        points=[SimpleNamespace(x=SimpleNamespace(value=0.0), y=SimpleNamespace(value=0.0))]
                    )
                ),
            )
        )
        edb.nets.nets = {}
        edb.padstacks.instances = {}
        edb.layout.primitives = []
        edb.components.instances = {}
        edb.padstacks.delete_batch_instances = MagicMock()
        edb.modeler.create_polygon = MagicMock()
        edb.components.refresh_components = MagicMock()

        cutout._create_cutout_multithread()

        # save_as must NOT have been called from within _create_cutout_multithread.
        edb.save_as.assert_not_called()
