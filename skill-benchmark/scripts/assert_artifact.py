from __future__ import annotations
import json, os, py_compile, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINTER = ROOT / "evaluator" / "lint_figure_code.py"


def provider_label(context) -> str | None:
    text = json.dumps(context.get("provider", {}), default=str)
    for label in ("candidate-00", "candidate-01", "candidate-02"):
        if label in text:
            return label
    return None


def workspace(context, label: str) -> Path:
    key = {
        "candidate-00": "control_workspace",
        "candidate-01": "scientific_workspace",
        "candidate-02": "kdense_workspace",
    }[label]
    return Path(context["vars"][key]).resolve()


def get_assert(output: str, context):
    label = provider_label(context)
    if label is None:
        return {"pass": False, "score": 0, "reason": "Could not resolve provider label"}
    ws = workspace(context, label)
    try:
        payload = json.loads(output)
    except Exception as exc:
        return {"pass": False, "score": 0, "reason": f"Final response is not JSON: {exc}"}

    script = ws / "answer.py"
    figure = ws / "answer.png"
    failures = []
    if payload.get("status") != "completed":
        failures.append(f"agent status={payload.get('status')}")
    if not script.is_file():
        failures.append("answer.py missing")
    if not figure.is_file():
        failures.append("answer.png missing")
    if failures:
        return {"pass": False, "score": 0, "reason": "; ".join(failures)}

    try:
        py_compile.compile(str(script), doraise=True)
    except Exception as exc:
        failures.append(f"Python compile failed: {exc}")

    rerun = subprocess.run(
        [sys.executable, str(script)], cwd=ws,
        env={**os.environ, "MPLBACKEND": "Agg", "PYTHONHASHSEED": "0"},
        text=True, capture_output=True, timeout=90,
    )
    if rerun.returncode != 0:
        failures.append(f"re-execution failed: {rerun.stderr[-800:]}")

    try:
        from PIL import Image
        with Image.open(figure) as im:
            im.verify()
        with Image.open(figure) as im:
            if im.width < 200 or im.height < 200:
                failures.append(f"figure too small: {im.width}x{im.height}")
    except Exception as exc:
        failures.append(f"PNG verification failed: {exc}")

    if LINTER.is_file():
        lint = subprocess.run(
            [sys.executable, str(LINTER), str(script)], cwd=ws,
            text=True, capture_output=True, timeout=60,
        )
        if lint.returncode != 0:
            failures.append(f"v0.7 AST linter failed: {(lint.stdout + lint.stderr)[-1200:]}")
    else:
        failures.append("v0.7 evaluator linter missing")

    return {
        "pass": not failures,
        "score": 1.0 if not failures else 0.0,
        "reason": "deterministic gates passed" if not failures else "; ".join(failures),
        "namedScores": {
            "artifact_exists": 1.0 if script.is_file() and figure.is_file() else 0.0,
            "deterministic_contract": 1.0 if not failures else 0.0,
        },
    }
