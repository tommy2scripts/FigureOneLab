#!/usr/bin/env python3
from __future__ import annotations
import json, os, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    ROOT / "benchmark" / "tasks" / "matplotbench.json",
    ROOT / "skill_templates" / "scientific-v0.7" / ".agents" / "skills" / "scientific-figure-design" / "SKILL.md",
    ROOT / "skill_templates" / "scientific-v0.7" / "sciplib" / "plot_utils.py",
    ROOT / "skill_templates" / "scientific-v0.7" / "scripts" / "lint_figure_code.py",
    ROOT / "skill_templates" / "scientific-v0.7" / "config" / "active_skills.json",
    ROOT / "skill_templates" / "kdense-v1.2" / ".agents" / "skills" / "scientific-visualization" / "SKILL.md",
    ROOT / "evaluator" / "lint_figure_code.py",
    ROOT / "promptfooconfig.yaml",
]


def out(*args: str) -> str | None:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None


def main() -> int:
    missing = [str(p.relative_to(ROOT)) for p in REQUIRED if not p.is_file()]
    node = out("node", "--version")
    promptfoo = out("npx", "promptfoo", "--version")
    registry_path = ROOT / "skill_templates" / "scientific-v0.7" / "config" / "active_skills.json"
    registry_ok = False
    registry = None
    if registry_path.is_file():
        registry = json.loads(registry_path.read_text())
        rec = registry.get("skills", {}).get("scientific-figure-design", {})
        registry_ok = (
            rec.get("champion_version") == "v0.7.0"
            and rec.get("status") == "production"
            and "sciplib.plot_utils" in rec.get("deterministic_modules", [])
            and "scripts/lint_figure_code.py" in rec.get("static_linters", [])
            and rec.get("gate_no_regression") is True
        )
    auth_hint = bool(os.getenv("OPENAI_API_KEY") or os.getenv("CODEX_API_KEY"))
    codex_home = Path(os.getenv("CODEX_HOME", str(Path.home() / ".codex"))).expanduser()
    chatgpt_login_hint = codex_home.exists() and any(codex_home.iterdir()) if codex_home.is_dir() else False
    tasks_count = None
    tasks = ROOT / "benchmark" / "tasks" / "matplotbench.json"
    if tasks.is_file():
        try:
            tasks_count = len(json.loads(tasks.read_text()))
        except Exception:
            tasks_count = -1
    report = {
        "ok": not missing and registry_ok and tasks_count == 100 and bool(node) and bool(promptfoo),
        "missing": missing,
        "registry_ok": registry_ok,
        "tasks_count": tasks_count,
        "node": node,
        "promptfoo": promptfoo,
        "python": sys.version.split()[0],
        "git_sha": out("git", "rev-parse", "HEAD"),
        "codex_auth_hint": {"api_key_present": auth_hint, "codex_home_nonempty": chatgpt_login_hint},
    }
    artifacts = ROOT / "artifacts"
    artifacts.mkdir(exist_ok=True)
    (artifacts / "preflight.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if not report["ok"]:
        return 2
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
