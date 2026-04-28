from collections import Counter
from pathlib import Path
import re
import subprocess
import sys

results = {}
for label, args in [
    ("default (reads setup.cfg)", []),
    ("--select D203,D212,D213,D413", ["--select=D203,D212,D213,D413"]),
    ("--select D203,D211,D213,D413", ["--select=D203,D211,D213,D413"]),
]:
    r = subprocess.run(
        [sys.executable, "-m", "pydocstyle"] + args + ["src/pyedb/"],
        capture_output=True,
        text=True,
        cwd=r"C:\Users\svandenb\PycharmProjects\pyedb",
    )
    out = r.stdout + r.stderr
    violations = [l for l in out.split("\n") if re.match(r"\s+D\d+", l)]
    rules = re.findall(r"\bD\d{3}\b", out)
    counts = Counter(rules)
    line = f"\n=== {label} ===\nViolations: {len(violations)}"
    for rule, c in counts.most_common():
        line += f"\n  {rule}: {c}"
    results[label] = line

report = "\n".join(results.values())
Path(r"C:\Users\svandenb\PycharmProjects\pyedb\pydoc_report.txt").write_text(report, encoding="utf-8")

print("Done - output written to pydoc_report.txt")
