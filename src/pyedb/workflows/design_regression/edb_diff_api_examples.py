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

"""
PyEDB Diff & Regression Tool  ·  v3.0  ·  Python API examples
==============================================================
These snippets show how to drive the tool programmatically instead of
(or alongside) the CLI — useful for CI pipelines, Jupyter notebooks,
custom reporting, and trend analysis.
"""

# ── Install dependencies ──────────────────────────────────────────────────────
# pip install pyedb pandas openpyxl rich pyyaml gitpython

# ─────────────────────────────────────────────────────────────────────────────
# 1. Basic diff (no Git, no DB)
# ─────────────────────────────────────────────────────────────────────────────
from edb_diff_regression import DiffConfig, run_diff, write_excel_report, write_json_report

cfg = DiffConfig(edb_version="2024.1")

report = run_diff(
    baseline_path="path/to/board_v1.aedb",
    modified_path="path/to/board_v2.aedb",
    cfg=cfg,
)

print(f"Total changes : {len(report.diffs)}")
print(f"EM sim needed : {report.em_required_count}")
print(f"Severity      : {report.severity_counts}")

write_excel_report(report, "diff_report.xlsx")
write_json_report(report, "diff_report.json")


# ─────────────────────────────────────────────────────────────────────────────
# 2. Diff with Git + database
# ─────────────────────────────────────────────────────────────────────────────
from edb_diff_regression import (
    DiffConfig,
    DiffDatabase,
    _capture_git_info,
    run_diff,
    write_excel_report,
)

cfg = DiffConfig(edb_version="2024.1", db_path="edb_history.db")
db = DiffDatabase("edb_history.db")

git_info = _capture_git_info(
    repo_path="/path/to/project",
    auto_commit=False,
)

report = run_diff(
    baseline_path="path/to/board_v1.aedb",
    modified_path="path/to/board_v2.aedb",
    cfg=cfg,
    db=db,
    git_info=git_info,
)

print(f"Saved as run_id={report.run_id}  branch={git_info.current_branch}")
write_excel_report(report, "diff_report.xlsx")
db.close()


# ─────────────────────────────────────────────────────────────────────────────
# 3. Inspect EM-critical changes
# ─────────────────────────────────────────────────────────────────────────────
from edb_diff_regression import DiffConfig, run_diff

report = run_diff("board_v1.aedb", "board_v2.aedb")

print(f"\n⚡ {len(report.em_critical_entries)} EM-critical change(s):\n")
for entry in report.em_critical_entries:
    reasons = ", ".join(entry.em_sim_reasons)
    print(f"  [{entry.category}]  {entry.item_name}  {entry.detail or entry.change_type}")
    print(f"    Reasons : {reasons}")
    print(f"    Delta   : {entry.baseline_value} → {entry.modified_value}")
    print()

# Filter to stackup changes only
stackup_em = [e for e in report.em_critical_entries if e.category == "Layer"]
print(f"Stackup-related EM flags: {len(stackup_em)}")


# ─────────────────────────────────────────────────────────────────────────────
# 4. Tune EM criticality thresholds
# ─────────────────────────────────────────────────────────────────────────────
from edb_diff_regression import DiffConfig, run_diff

cfg = DiffConfig(
    # Tighter thresholds for a high-frequency mmWave design
    em_layer_thickness_pct=2.0,  # flag any >2% thickness change (default 5%)
    em_trace_width_pct=5.0,  # flag any >5% trace narrowing (default 10%)
    em_via_drill_pct=10.0,  # flag any >10% drill change   (default 15%)
    em_component_move_mm=0.1,  # stricter placement tolerance (default 0.5)
    # Add project-specific net name patterns
    em_rf_net_patterns=["RF", "ANT", "MMWAVE", "V_BAND", "DIFF", "CLK", "TX", "RX"],
    em_power_net_patterns=["VDD", "VCC", "GND", "VSS", "VBAT", "PA_VCC"],
    em_hs_comp_patterns=["U", "IC", "PA", "LNA", "MIXER", "PLL", "FPGA"],
)

report = run_diff("board_v1.aedb", "board_v2.aedb", cfg=cfg)
print(f"EM flags with tight thresholds: {report.em_required_count}")


# ─────────────────────────────────────────────────────────────────────────────
# 5. Save and manage baseline references
# ─────────────────────────────────────────────────────────────────────────────
from edb_diff_regression import DiffConfig, DiffDatabase, save_baseline_reference

db = DiffDatabase("edb_history.db")
cfg = DiffConfig(edb_version="2024.1")

# Save a golden snapshot
ref_id = save_baseline_reference(
    db=db,
    name="golden_v1.2",
    design_path="path/to/board_release.aedb",
    cfg=cfg,
    tag="release",
    notes="Signed off by SI team — board rev C",
)
print(f"Saved baseline ref id={ref_id}")

# List all stored baselines
for ref in db.list_baseline_references():
    print(f"  [{ref['id']}] {ref['name']:20s}  {ref['stored_at'][:10]}  {ref.get('tag', '')}")

# Load a specific snapshot back (returns dict with 'snapshot' key)
ref_data = db.load_baseline_reference("golden_v1.2")
if ref_data:
    snap = ref_data["snapshot"]
    print(f"\ngolden_v1.2 has {len(snap.get('nets', {}))} nets in snapshot")

db.close()


# ─────────────────────────────────────────────────────────────────────────────
# 6. Validate a design against all stored baselines
# ─────────────────────────────────────────────────────────────────────────────
from edb_diff_regression import (
    DiffConfig,
    DiffDatabase,
    validate_against_baselines,
    write_excel_report,
)

db = DiffDatabase("edb_history.db")
cfg = DiffConfig(edb_version="2024.1")

validations, sub_reports = validate_against_baselines(
    modified_path="path/to/board_candidate.aedb",
    db=db,
    cfg=cfg,
    # baseline_names = ["golden_v1.0", "golden_v1.2"],  # optional filter
)

for vr in validations:
    status = "PASS" if vr.passed else "FAIL"
    print(
        f"  {vr.baseline_name:20s}  {status}  "
        f"changes={vr.total_changes}  critical={vr.critical_count}  "
        f"em_required={vr.em_required_count}"
    )

# Build a combined report
from edb_diff_regression import DiffReport

combined = DiffReport(
    baseline_path="(all baselines)",
    modified_path="path/to/board_candidate.aedb",
)
combined.baseline_validations = validations
for sr in sub_reports:
    combined.diffs.extend(sr.diffs)
combined.em_critical_entries = [d for d in combined.diffs if d.em_sim_required]

write_excel_report(combined, "validation_report.xlsx")
db.close()


# ─────────────────────────────────────────────────────────────────────────────
# 7. Run history and trend analysis
# ─────────────────────────────────────────────────────────────────────────────
from edb_diff_regression import DiffDatabase

db = DiffDatabase("edb_history.db")

# Print last 10 runs
print("Last 10 runs:\n")
for row in db.get_run_history(limit=10):
    print(
        f"  [{row['id']:3d}] {row['generated_at'][:16]}  "
        f"critical={row['critical_count']}  "
        f"em={row['em_required']}  "
        f"fails={row['reg_fail']}  "
        f"branch={row['git_branch'] or '—'}"
    )

# Trend: EM-required count over last 20 runs (for plotting)
trend = db.get_trend("em_required", last_n=20)
print("\nEM-required trend:")
for row in trend:
    bar = "█" * row["em_required"]
    print(f"  {row['generated_at'][:10]}  {row['em_required']:3d}  {bar}")

# Query directly with pandas
import sqlite3

import pandas as pd

conn = sqlite3.connect("edb_history.db")
df = pd.read_sql("SELECT * FROM runs ORDER BY id DESC", conn)
print(f"\nDataFrame shape: {df.shape}")
print(df[["id", "generated_at", "critical_count", "em_required", "git_branch"]].head())
conn.close()

db.close()


# ─────────────────────────────────────────────────────────────────────────────
# 8. CI pipeline integration example
# ─────────────────────────────────────────────────────────────────────────────
import sys

from edb_diff_regression import (
    DiffConfig,
    DiffDatabase,
    _capture_git_info,
    run_diff,
    validate_against_baselines,
    write_excel_report,
    write_json_report,
)


def ci_check(baseline: str, modified: str, db_path: str, repo: str) -> int:
    """
    Returns exit code: 0 = pass, 1 = fail.
    Suitable for use in Jenkins, GitHub Actions, GitLab CI, etc.
    """
    cfg = DiffConfig(edb_version="2024.1")
    db = DiffDatabase(db_path)
    git_info = _capture_git_info(repo)

    # Run diff
    report = run_diff(baseline, modified, cfg=cfg, db=db, git_info=git_info)
    write_excel_report(report, "ci_diff_report.xlsx")
    write_json_report(report, "ci_diff_report.json")

    # Gate 1: no Critical-severity diffs
    critical = report.severity_counts.get("Critical", 0)
    if critical > 0:
        print(f"CI FAIL: {critical} Critical-severity change(s) detected.")
        db.close()
        return 1

    # Gate 2: no EM re-simulation required
    if report.em_required_count > 0:
        print(f"CI FAIL: {report.em_required_count} change(s) require EM re-simulation.")
        db.close()
        return 1

    # Gate 3: validate against all stored baselines
    validations, _ = validate_against_baselines(modified, db, cfg)
    if any(not v.passed for v in validations):
        failed = [v.baseline_name for v in validations if not v.passed]
        print(f"CI FAIL: Baseline validation failed for: {', '.join(failed)}")
        db.close()
        return 1

    print("CI PASS: all checks passed.")
    db.close()
    return 0


if __name__ == "__main__":
    exit_code = ci_check(
        baseline="path/to/board_v1.aedb",
        modified="path/to/board_v2.aedb",
        db_path="edb_history.db",
        repo="/path/to/project",
    )
    sys.exit(exit_code)
