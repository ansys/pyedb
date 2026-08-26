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

"""PCIe Gen5 via-stub optimization."""

from pyedb import Edb

PCIE_NETS = ["PCIE_RX0_P", "PCIE_RX0_N"]
TARGET_LAYER = "L6"


def main():
    edb = Edb("generic_board.aedb")
    try:
        vias = edb.padstacks.get_via_instance_from_net(PCIE_NETS)
        defs = sorted({v.padstack_definition for v in vias})
        edb.padstacks.create_dielectric_filled_backdrills(
            layer=TARGET_LAYER,
            diameter="0.25mm",
            material="EPON_827",
            permittivity=3.8,
            dielectric_loss_tangent=0.015,
            padstack_definition=defs,
            nets=PCIE_NETS,
        )
        edb.save()
    finally:
        edb.close()


if __name__ == "__main__":
    main()
