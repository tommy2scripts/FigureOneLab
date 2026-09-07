#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, urllib.request
from pathlib import Path

COMMIT = "9cafa262aae7bdf85fccf6d02b2153fb772bc376"
URL = f"https://raw.githubusercontent.com/thunlp/MatPlotAgent/{COMMIT}/benchmark_data/benchmark_instructions.json"
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "benchmark" / "tasks" / "matplotbench.json"
PROV = ROOT / "benchmark" / "tasks" / "PROVENANCE.json"


def main() -> None:
    with urllib.request.urlopen(URL, timeout=30) as r:
        raw = r.read()
    rows = json.loads(raw)
    tasks = [{"id": int(x["id"]), "instruction": x["simple_instruction"]} for x in rows]
    if len(tasks) != 100 or len({x['id'] for x in tasks}) != 100:
        raise SystemExit(f"Expected 100 unique MatPlotBench tasks, got {len(tasks)}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(tasks, indent=2) + "\n")
    PROV.write_text(json.dumps({
        "source_repository": "thunlp/MatPlotAgent",
        "source_commit": COMMIT,
        "source_path": "benchmark_data/benchmark_instructions.json",
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "exported_fields": ["id", "simple_instruction"],
        "expert_instruction_excluded_from_generation_workspace": True
    }, indent=2) + "\n")
    print(f"Staged {len(tasks)} MatPlotBench tasks at {OUT}")

if __name__ == "__main__":
    main()
