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


GRPC_GENERAL_WARNING = (
    "This version of the Ansys Electronics Database (EDB) is compatible with the gRPC "
    "interface. You can enable gRPC by passing ``grpc=True`` when instantiating the Edb object. "
    "For more information please check this link: https://edb.docs.pyansys.com/version/dev/grpc_api/index.html"
)

GRPC_BETA_WARNING = (
    "You are using PyEDB with grpc, which is currently in beta. Some feature might be missing or not "
    "working as expected. Please report any issue you find to the PyEDB team."
)

GRPC_NOT_SUPPORTED_WARNING = (
    f"gRPC is now the default backend selection for PyEDB is and not supported for AEDT "
    f"version 2025.2 and earlier."
    f"Please use AEDT version 2026.1 or later to enable gRPC functionality, "
    f"or set grpc=False to use the DotNet backend. Note DotNet will be deprecated and gRPC will be the long"
    f" term supported version."
)

DOTNET_USAGE_WARNING = (
    "DotNet version of PyEDB used. Please note that this version of PyEDB is planned to be deprecated in the future "
    "and gRPC version will remains the long term supported one. Upgrade to ANSYS release version 2026.1.2 or later"
    "for fast grpc performances."
)
