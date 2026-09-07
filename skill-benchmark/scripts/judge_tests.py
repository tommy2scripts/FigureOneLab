from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / ".blind_judge" / "judge_cases.json"

RUBRIC = """You are a blinded scientific-figure evaluator. You do not know which skill produced any candidate and must not infer identity from style. Inspect all three rendered figures and their answer.py files. Use the task plus the hidden expert instruction only as evaluation criteria; do not reward implementation mimicry when another scientifically correct implementation satisfies the task.

For each candidate, score 0-4 on:
1. scientific_correctness: truthful data/uncertainty/statistical semantics; no fabricated or misleading inference.
2. task_requirements: requested elements, data, layout, labels, and reproducibility.
3. visual_quality: legibility, clipping/overlap, hierarchy, contrast/accessibility, and publication-readiness for the stated task.

Set critical_error=true for a material scientific/data-integrity failure, fabricated result, incorrect statistic, silent omission of requested evidence, or figure that cannot support the requested inference.

Then compare candidate_1 vs candidate_2 only and set pairwise_preference to candidate_1, candidate_2, or tie. candidate_3 is scored absolutely for no-skill uplift analysis and does not participate in that pairwise preference. Keep rationale concise and evidence-based."""


def create_tests(config=None):
    if not CASES.is_file():
        raise RuntimeError("Missing blinded cases; run python3 scripts/prepare_blind_judge.py")
    rows = json.loads(CASES.read_text())
    tests = []
    for row in rows:
        ws = Path(row["judge_workspace"])
        text = (
            RUBRIC
            + "\n\nTASK:\n" + row["task"]
            + "\n\nEXPERT CRITERIA (not shown to candidates):\n" + row["expert_instruction"]
            + "\n\nCandidate code files are candidate_1/answer.py, candidate_2/answer.py, and candidate_3/answer.py."
        )
        prompt_items = [
            {"type": "text", "text": text + "\n\nCandidate 1 rendered figure:"},
            {"type": "local_image", "path": str((ws / "candidate_1" / "answer.png").resolve())},
            {"type": "text", "text": "Candidate 2 rendered figure:"},
            {"type": "local_image", "path": str((ws / "candidate_2" / "answer.png").resolve())},
            {"type": "text", "text": "Candidate 3 rendered figure:"},
            {"type": "local_image", "path": str((ws / "candidate_3" / "answer.png").resolve())},
        ]
        tests.append({
            "description": row["case_id"],
            "vars": {
                "judge_workspace": row["judge_workspace"],
                "judge_input": json.dumps(prompt_items),
                "case_id": row["case_id"],
            },
        })
    return tests
