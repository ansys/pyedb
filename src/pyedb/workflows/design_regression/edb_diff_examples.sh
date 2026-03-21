#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
# PyEDB Diff & Regression Tool  ·  v3.0  ·  Example run scripts
# Edit the paths at the top of each section, then run the relevant block.
# ──────────────────────────────────────────────────────────────────────────────

# ── Shared variables (edit these) ─────────────────────────────────────────────
BASELINE="/path/to/board_v1.aedb"
MODIFIED="/path/to/board_v2.aedb"
GIT_REPO="/path/to/your/project"
DB="edb_history.db"
CONFIG="edb_diff_config.yaml"


# ══════════════════════════════════════════════════════════════════════════════
# 1. QUICK DEMO  (no EDB files needed — great for first-time exploration)
# ══════════════════════════════════════════════════════════════════════════════
python edb_diff_regression.py \
    --demo \
    --report demo_report.xlsx


# ══════════════════════════════════════════════════════════════════════════════
# 2. BASIC DIFF  (no Git, no DB)
# ══════════════════════════════════════════════════════════════════════════════
python edb_diff_regression.py \
    --baseline "$BASELINE" \
    --modified "$MODIFIED" \
    --report   diff_report.xlsx \
    --json     diff_report.json


# ══════════════════════════════════════════════════════════════════════════════
# 3. DIFF WITH CUSTOM CONFIG
# ══════════════════════════════════════════════════════════════════════════════
python edb_diff_regression.py \
    --baseline "$BASELINE" \
    --modified "$MODIFIED" \
    --config   "$CONFIG" \
    --report   diff_report.xlsx


# ══════════════════════════════════════════════════════════════════════════════
# 4. DIFF + GIT TRACKING  (captures branch, commit, dirty status)
# ══════════════════════════════════════════════════════════════════════════════
python edb_diff_regression.py \
    --baseline  "$BASELINE" \
    --modified  "$MODIFIED" \
    --git-repo  "$GIT_REPO" \
    --report    diff_report.xlsx


# ══════════════════════════════════════════════════════════════════════════════
# 5. DIFF + GIT AUTO-COMMIT  (commits dirty tree before diff)
# ══════════════════════════════════════════════════════════════════════════════
python edb_diff_regression.py \
    --baseline   "$BASELINE" \
    --modified   "$MODIFIED" \
    --git-repo   "$GIT_REPO" \
    --git-commit \
    --report     diff_report.xlsx


# ══════════════════════════════════════════════════════════════════════════════
# 6. DIFF + DATABASE  (persist every run to SQLite)
# ══════════════════════════════════════════════════════════════════════════════
python edb_diff_regression.py \
    --baseline "$BASELINE" \
    --modified "$MODIFIED" \
    --db       "$DB" \
    --report   diff_report.xlsx


# ══════════════════════════════════════════════════════════════════════════════
# 7. FULL RUN  (Git + DB + custom config + verbose logging)
# ══════════════════════════════════════════════════════════════════════════════
python edb_diff_regression.py \
    --baseline  "$BASELINE" \
    --modified  "$MODIFIED" \
    --config    "$CONFIG" \
    --git-repo  "$GIT_REPO" \
    --db        "$DB" \
    --report    full_diff_report.xlsx \
    --json      full_diff_report.json \
    --verbose


# ══════════════════════════════════════════════════════════════════════════════
# 8. FULL RUN + S-PARAMETER SIMULATION  (requires AEDT licence)
# ══════════════════════════════════════════════════════════════════════════════
python edb_diff_regression.py \
    --baseline  "$BASELINE" \
    --modified  "$MODIFIED" \
    --config    "$CONFIG" \
    --simulate \
    --freq-ghz  20 \
    --git-repo  "$GIT_REPO" \
    --db        "$DB" \
    --report    sim_diff_report.xlsx \
    --json      sim_diff_report.json


# ══════════════════════════════════════════════════════════════════════════════
# 9. SAVE A GOLDEN BASELINE REFERENCE
# ══════════════════════════════════════════════════════════════════════════════
python edb_diff_regression.py \
    --save-baseline  "golden_v1.0" \
    --modified       "$MODIFIED" \
    --db             "$DB" \
    --git-repo       "$GIT_REPO" \
    --baseline-tag   "release" \
    --baseline-notes "Signed off by SI team — board rev C"


# ══════════════════════════════════════════════════════════════════════════════
# 10. LIST STORED BASELINE REFERENCES
# ══════════════════════════════════════════════════════════════════════════════
python edb_diff_regression.py \
    --db "$DB" \
    --list-baselines


# ══════════════════════════════════════════════════════════════════════════════
# 11. VALIDATE MODIFIED DESIGN AGAINST ALL STORED BASELINES
# ══════════════════════════════════════════════════════════════════════════════
python edb_diff_regression.py \
    --validate-baselines \
    --modified "$MODIFIED" \
    --db       "$DB" \
    --report   validation_report.xlsx


# ══════════════════════════════════════════════════════════════════════════════
# 12. VALIDATE AGAINST SPECIFIC NAMED BASELINES ONLY
# ══════════════════════════════════════════════════════════════════════════════
python edb_diff_regression.py \
    --validate-baselines \
    --baseline-names golden_v1.0 golden_v1.2 \
    --modified "$MODIFIED" \
    --db       "$DB" \
    --report   targeted_validation.xlsx


# ══════════════════════════════════════════════════════════════════════════════
# 13. SHOW RUN HISTORY FROM DATABASE
# ══════════════════════════════════════════════════════════════════════════════
python edb_diff_regression.py \
    --db "$DB" \
    --history
