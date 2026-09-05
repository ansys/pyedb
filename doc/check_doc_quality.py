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

#!/usr/bin/env python
"""Documentation quality gate.

Builds the Sphinx documentation from a clean state and enforces a warning-count ceiling so that
the numeric baseline captured in ``doc_audit.md`` cannot silently regress. This script is
intentionally self-contained (does not depend on the internals of the ``ansys/actions/doc-build``
reusable action) so it can be run identically in CI and locally.

Usage
-----
python doc/check_doc_quality.py [--max-warnings N] [--max-errors N]

Exit codes
----------
0 : build succeeded and warning/error counts are within the configured ceiling
1 : build succeeded but the warning or error count ceiling was exceeded
2 : the Sphinx build itself failed to run
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import subprocess
import sys

# Baseline ceilings, ratcheted down as real fixes land. See doc_audit.md section 10 for the
# measured history of these numbers; do not raise these values to make a broken build pass.
DEFAULT_MAX_WARNINGS = 1830
DEFAULT_MAX_ERRORS = 90

REPO_ROOT = Path(__file__).resolve().parent.parent
DOC_SOURCE = REPO_ROOT / "doc" / "source"
BUILD_OUTPUT = REPO_ROOT / "doc" / "_build" / "quality_gate_html"
LOG_FILE = REPO_ROOT / "doc" / "_build" / "quality_gate_errors.txt"


def _clean_autosummary_dirs() -> None:
    """Remove stale sphinx.ext.autosummary stub directories that can otherwise cause
    phantom orphan-page warnings across unrelated runs (see AGENTS.md)."""
    for path in DOC_SOURCE.rglob("_autosummary"):
        if path.is_dir():
            for child in sorted(path.rglob("*"), reverse=True):
                if child.is_file():
                    child.unlink()
                else:
                    child.rmdir()
            path.rmdir()


def run_build() -> tuple[int, list[str]]:
    """Run a clean Sphinx HTML build and return (return_code, warning_lines)."""
    _clean_autosummary_dirs()
    BUILD_OUTPUT.mkdir(parents=True, exist_ok=True)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable,
        "-m",
        "sphinx",
        "-b",
        "html",
        str(DOC_SOURCE),
        str(BUILD_OUTPUT),
        "-w",
        str(LOG_FILE),
        "-q",
        "-E",  # force a full re-read; a cached doctree can mask or fake warning-count changes
    ]
    result = subprocess.run(cmd, cwd=REPO_ROOT, check=False)
    warning_lines = []
    if LOG_FILE.exists():
        warning_lines = LOG_FILE.read_text(encoding="utf-8", errors="replace").splitlines()
    return result.returncode, warning_lines


def count_issues(lines: list[str]) -> tuple[int, int]:
    warnings = sum(1 for line in lines if re.search(r"\bWARNING:", line))
    errors = sum(1 for line in lines if re.search(r"\bERROR:", line))
    return warnings, errors


def find_new_orphans(lines: list[str]) -> list[str]:
    """Return orphan-page warnings for hand-authored pages (excludes AutoAPI-generated pages,
    which are intentionally excluded from navigation)."""
    return [
        line for line in lines if "toc.not_included" in line and "autoapi" not in line and "_autosummary" not in line
    ]


def find_broken_refs(lines: list[str]) -> list[str]:
    """Return broken internal document/label reference warnings (ref.doc / ref.ref)."""
    return [line for line in lines if "[ref.doc]" in line or "[ref.ref]" in line]


def write_job_summary(
    warnings: int,
    errors: int,
    orphans: list[str],
    broken_refs: list[str],
    max_warnings: int,
    max_errors: int,
) -> None:
    """Write a Markdown summary to ``$GITHUB_STEP_SUMMARY`` when running in GitHub Actions, so
    documentation quality metrics are visible directly on the workflow run page rather than only
    buried in a log."""
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return

    def _status(value: int, ceiling: int) -> str:
        return "✅" if value <= ceiling else "❌"

    def _status_zero(count: int) -> str:
        return "✅" if count == 0 else "❌"

    lines = [
        "## Documentation quality gate",
        "",
        "| Metric | Value | Ceiling | Status |",
        "|---|---|---|---|",
        f"| Sphinx warnings | {warnings} | {max_warnings} | {_status(warnings, max_warnings)} |",
        f"| Sphinx errors | {errors} | {max_errors} | {_status(errors, max_errors)} |",
        f"| Hand-authored orphan pages | {len(orphans)} | 0 | {_status_zero(len(orphans))} |",
        f"| Broken internal doc/label references | {len(broken_refs)} | 0 | {_status_zero(len(broken_refs))} |",
        "",
        "Baseline history and methodology: see `doc_audit.md`, section 10.",
    ]
    with open(summary_path, "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-warnings", type=int, default=DEFAULT_MAX_WARNINGS)
    parser.add_argument("--max-errors", type=int, default=DEFAULT_MAX_ERRORS)
    args = parser.parse_args()

    return_code, lines = run_build()
    if return_code != 0 and not lines:
        print("Sphinx build failed to produce any warning log; treating as a hard failure.")
        return 2

    warnings, errors = count_issues(lines)
    orphans = find_new_orphans(lines)
    broken_refs = find_broken_refs(lines)

    print(f"Sphinx warnings: {warnings} (ceiling: {args.max_warnings})")
    print(f"Sphinx errors:   {errors} (ceiling: {args.max_errors})")
    print(f"Hand-authored orphan pages: {len(orphans)} (must be 0)")
    print(f"Broken internal doc/label references: {len(broken_refs)} (must be 0)")

    write_job_summary(warnings, errors, orphans, broken_refs, args.max_warnings, args.max_errors)

    failed = False
    if warnings > args.max_warnings:
        print(f"FAIL: warning count {warnings} exceeds ceiling {args.max_warnings}.")
        failed = True
    if errors > args.max_errors:
        print(f"FAIL: error count {errors} exceeds ceiling {args.max_errors}.")
        failed = True
    if orphans:
        print("FAIL: hand-authored pages are unreachable from any toctree:")
        for line in orphans:
            print(f"  {line}")
        failed = True
    if broken_refs:
        print("FAIL: broken internal document/label references:")
        for line in broken_refs:
            print(f"  {line}")
        failed = True

    if failed:
        return 1

    print("Documentation quality gate passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
