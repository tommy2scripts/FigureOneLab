#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, shutil, subprocess, tempfile
from pathlib import Path

REPO = "https://github.com/K-Dense-AI/scientific-agent-skills.git"
COMMIT = "1e5eeffbdad3749125afe7ab48a39694e27f181c"
SOURCE = Path("skills/scientific-visualization")
ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "skill_templates" / "kdense-v1.2" / ".agents" / "skills" / "scientific-visualization"
PROV = ROOT / "skill_templates" / "kdense-v1.2" / "PROVENANCE.json"


def tree_hash(path: Path) -> str:
    h = hashlib.sha256()
    for f in sorted(p for p in path.rglob('*') if p.is_file()):
        h.update(str(f.relative_to(path)).encode())
        h.update(b'\0')
        h.update(f.read_bytes())
    return h.hexdigest()


def main() -> None:
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        subprocess.run(["git", "clone", "--filter=blob:none", "--no-checkout", REPO, str(td / "repo")], check=True)
        subprocess.run(["git", "-C", str(td / "repo"), "sparse-checkout", "set", str(SOURCE)], check=True)
        subprocess.run(["git", "-C", str(td / "repo"), "checkout", COMMIT], check=True)
        src = td / "repo" / SOURCE
        if not (src / "SKILL.md").is_file():
            raise SystemExit("Pinned K-Dense skill is missing SKILL.md")
        if DEST.exists():
            shutil.rmtree(DEST)
        DEST.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src, DEST)
    text = (DEST / "SKILL.md").read_text(errors="replace")
    if 'version: "1.2"' not in text and "version: '1.2'" not in text:
        raise SystemExit("Pinned K-Dense skill did not declare version 1.2")
    PROV.parent.mkdir(parents=True, exist_ok=True)
    PROV.write_text(json.dumps({
        "source_repository": "K-Dense-AI/scientific-agent-skills",
        "source_commit": COMMIT,
        "source_path": str(SOURCE),
        "package_sha256": tree_hash(DEST)
    }, indent=2) + "\n")
    print(f"Staged K-Dense scientific-visualization v1.2 at {DEST}")

if __name__ == "__main__":
    main()
