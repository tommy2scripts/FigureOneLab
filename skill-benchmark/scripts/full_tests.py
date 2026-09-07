from __future__ import annotations
import json, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "benchmark" / "tasks" / "matplotbench.json"
TEMPLATES = ROOT / "skill_templates"
RUNS = ROOT / ".benchmark_runs"


def copy_template(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.exists():
        shutil.copytree(src, dst)
    else:
        dst.mkdir(parents=True)


def create_tests(config=None):
    config = config or {}
    max_cases = int(config.get("max_cases", 100))
    repeats = int(config.get("repeats", 3))
    if not TASKS.is_file():
        raise RuntimeError(f"Missing task set: {TASKS}; run npm run fetch:tasks")
    scientific_template = TEMPLATES / "scientific-v0.7"
    kdense_template = TEMPLATES / "kdense-v1.2"
    for required in [
        scientific_template / ".agents" / "skills" / "scientific-figure-design" / "SKILL.md",
        scientific_template / "sciplib" / "plot_utils.py",
        scientific_template / "scripts" / "lint_figure_code.py",
        kdense_template / ".agents" / "skills" / "scientific-visualization" / "SKILL.md",
    ]:
        if not required.is_file():
            raise RuntimeError(f"Missing staged candidate asset: {required}")

    tasks = json.loads(TASKS.read_text())[:max_cases]
    cases = []
    for task in tasks:
        tid = int(task["id"])
        for rep in range(1, repeats + 1):
            base = RUNS / f"task-{tid:03d}" / f"rep-{rep}"
            control = base / "candidate-00"
            scientific = base / "candidate-01"
            kdense = base / "candidate-02"
            copy_template(Path("/__missing_control_template__"), control)
            copy_template(scientific_template, scientific)
            copy_template(kdense_template, kdense)
            metadata = {"task_id": tid, "repeat_id": rep, "instruction": task["instruction"]}
            for p in [control, scientific, kdense]:
                (p / "task.json").write_text(json.dumps(metadata, indent=2) + "\n")
            cases.append({
                "description": f"task-{tid:03d}-rep-{rep}",
                "vars": {
                    "task_id": str(tid),
                    "repeat_id": str(rep),
                    "task": task["instruction"],
                    "control_workspace": str(control.resolve()),
                    "scientific_workspace": str(scientific.resolve()),
                    "kdense_workspace": str(kdense.resolve()),
                },
            })
    return cases
