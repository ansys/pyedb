# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT

"""Refresh ignored local RHI shader packs for source-tree development.

Run ``python tools/bake_viewer_shaders.py`` after changing shader sources.
End users do not need this tool or the Vulkan SDK.
"""

from pathlib import Path
import sys


def main():
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "_build_backend"))
    from pyedb_shader_tools import SHADER_DIRECTORY, bake_shaders

    for output in bake_shaders(root / SHADER_DIRECTORY):
        print(output.name)


if __name__ == "__main__":
    main()
