#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "skill_templates" / "scientific-v0.7"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def locate_manifest(src: Path) -> Path:
    candidates = [
        src / "skills" / "scientific-figure-design" / "v0.7.0.md",
        src / "scientific-figure-design" / "v0.7.0.md",
    ]
    for p in candidates:
        if p.is_file():
            return p
    raise FileNotFoundError("Could not locate scientific-figure-design v0.7.0 manifest")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-root", default=os.getenv("SCIENTIFIC_FIGURE_ROOT"))
    args = ap.parse_args()
    if not args.source_root:
        raise SystemExit("Set SCIENTIFIC_FIGURE_ROOT to the workspace containing v0.7.0")
    src = Path(args.source_root).expanduser().resolve()
    manifest = locate_manifest(src)
    required = {
        "manifest": manifest,
        "plot_utils": src / "sciplib" / "plot_utils.py",
        "linter": src / "scripts" / "lint_figure_code.py",
        "active_skills": src / "config" / "active_skills.json",
    }
    missing = [name for name, p in required.items() if not p.is_file()]
    if missing:
        raise SystemExit(f"v0.7.0 source is incomplete; missing: {', '.join(missing)}")

    active = json.loads(required["active_skills"].read_text())
    rec = active.get("skills", {}).get("scientific-figure-design", {})
    if rec.get("champion_version") != "v0.7.0" or rec.get("status") != "production":
        raise SystemExit("active_skills.json does not report v0.7.0 as production champion")
    if "sciplib.plot_utils" not in rec.get("deterministic_modules", []):
        raise SystemExit("active_skills.json is missing sciplib.plot_utils")
    if "scripts/lint_figure_code.py" not in rec.get("static_linters", []):
        raise SystemExit("active_skills.json is missing scripts/lint_figure_code.py")

    if DEST.exists():
        shutil.rmtree(DEST)
    skill_dir = DEST / ".agents" / "skills" / "scientific-figure-design"
    skill_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(manifest, skill_dir / "SKILL.md")

    (DEST / "sciplib").mkdir(parents=True, exist_ok=True)
    shutil.copy2(required["plot_utils"], DEST / "sciplib" / "plot_utils.py")
    init = src / "sciplib" / "__init__.py"
    if init.is_file():
        shutil.copy2(init, DEST / "sciplib" / "__init__.py")
    else:
        (DEST / "sciplib" / "__init__.py").write_text("")

    (DEST / "scripts").mkdir(parents=True, exist_ok=True)
    shutil.copy2(required["linter"], DEST / "scripts" / "lint_figure_code.py")
    (DEST / "config").mkdir(parents=True, exist_ok=True)
    shutil.copy2(required["active_skills"], DEST / "config" / "active_skills.json")
    for rel in ["config/benchmark_config.yaml", "skills/manifest.json"]:
        p = src / rel
        if p.is_file():
            out = DEST / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, out)

    evaluator = ROOT / "evaluator"
    evaluator.mkdir(parents=True, exist_ok=True)
    shutil.copy2(required["linter"], evaluator / "lint_figure_code.py")

    provenance = {
        "candidate": "scientific-figure-design",
        "version": "v0.7.0",
        "source_root": str(src),
        "files": {name: {"path": str(p), "sha256": sha256(p)} for name, p in required.items()},
        "registry": rec,
    }
    (DEST / "PROVENANCE.json").write_text(json.dumps(provenance, indent=2) + "\n")
    print(f"Staged promoted scientific-figure-design v0.7.0 from {src}")

if __name__ == "__main__":
    main()
