#!/usr/bin/env python3
from __future__ import annotations
import json, shutil, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / ".benchmark_runs"
AUDIT = ROOT / ".blind_judge"
ARTIFACTS = ROOT / "artifacts"
COMMIT = "9cafa262aae7bdf85fccf6d02b2153fb772bc376"
URL = f"https://raw.githubusercontent.com/thunlp/MatPlotAgent/{COMMIT}/benchmark_data/benchmark_instructions.json"


def main() -> None:
    with urllib.request.urlopen(URL, timeout=30) as r:
        refs = {int(x["id"]): x for x in json.loads(r.read())}
    tasks = json.loads((ROOT / "benchmark" / "tasks" / "matplotbench.json").read_text())
    if AUDIT.exists():
        shutil.rmtree(AUDIT)
    AUDIT.mkdir(parents=True)
    ARTIFACTS.mkdir(exist_ok=True)
    cases, mapping = [], {}
    for task in tasks:
        tid = int(task["id"])
        expert = refs[tid]["expert_instruction"]
        for rep in range(1, 4):
            src_base = RUNS / f"task-{tid:03d}" / f"rep-{rep}"
            sources = {
                "control": src_base / "candidate-00",
                "scientific-v0.7": src_base / "candidate-01",
                "kdense-v1.2": src_base / "candidate-02",
            }
            missing = [f"{arm}/{name}" for arm, p in sources.items() for name in ("answer.py", "answer.png") if not (p / name).is_file()]
            if missing:
                raise SystemExit(f"Cannot prepare judge case task={tid} rep={rep}; missing {missing}")
            for order, ordered in [
                ("ab", ["scientific-v0.7", "kdense-v1.2", "control"]),
                ("ba", ["kdense-v1.2", "scientific-v0.7", "control"]),
            ]:
                case_id = f"task-{tid:03d}-rep-{rep}-{order}"
                ws = AUDIT / case_id
                ws.mkdir(parents=True)
                for i, arm in enumerate(ordered, 1):
                    dst = ws / f"candidate_{i}"
                    dst.mkdir()
                    shutil.copy2(sources[arm] / "answer.py", dst / "answer.py")
                    shutil.copy2(sources[arm] / "answer.png", dst / "answer.png")
                cases.append({
                    "case_id": case_id,
                    "task_id": tid,
                    "repeat_id": rep,
                    "order": order,
                    "judge_workspace": str(ws.resolve()),
                    "task": task["instruction"],
                    "expert_instruction": expert,
                })
                mapping[case_id] = {f"candidate_{i}": arm for i, arm in enumerate(ordered, 1)}
    (AUDIT / "judge_cases.json").write_text(json.dumps(cases, indent=2) + "\n")
    (ARTIFACTS / "restricted_blind_map.json").write_text(json.dumps(mapping, indent=2) + "\n")
    print(f"Prepared {len(cases)} blinded judge cases")

if __name__ == "__main__":
    main()
