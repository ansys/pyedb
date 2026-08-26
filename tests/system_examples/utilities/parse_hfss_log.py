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

"""Parse an HFSS solver log and export a CI-friendly JSON summary."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pyedb.workflows.utilities.hfss_log_parser import HFSSLogParser


def parse_hfss_log(log_file: Path, output_dir: Path) -> tuple[dict, bool]:
    parsed = HFSSLogParser(log_file).parse()
    data = parsed.to_dict()
    data["completed"] = parsed.is_completed()
    data["converged"] = parsed.is_converged()
    data["errors"] = parsed.errors()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "hfss_run.json"
    output_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    success = data["completed"] and data["converged"] and not data["errors"]
    return data, success


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("log_file", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("sipi_output"))
    args = parser.parse_args()
    data, success = parse_hfss_log(args.log_file, args.output_dir)
    print(json.dumps(data, indent=2))
    raise SystemExit(0 if success else 1)


if __name__ == "__main__":
    main()
