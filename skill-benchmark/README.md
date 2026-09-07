# Scientific Figure Skill Benchmark

Three-arm controlled evaluation:

- `candidate-00`: no scientific visualization skill (control)
- `candidate-01`: `scientific-figure-design` **v0.7.0** (active champion)
- `candidate-02`: K-Dense `scientific-visualization` **v1.2** pinned to commit `1e5eeffbdad3749125afe7ab48a39694e27f181c`

Task source: MatPlotBench 100 human-verified plotting tasks pinned to MatPlotAgent commit `9cafa262aae7bdf85fccf6d02b2153fb772bc376`.

## Canonical experiment size

100 tasks × 3 replicates × 3 arms = **900 generation executions**.

The no-skill arm measures absolute skill uplift; candidate-01 vs candidate-02 measures relative skill quality.

## v0.7.0 source contract

The benchmark does **not** check the private/local v0.7.0 implementation into this repository. Stage it from the Work/Codex workspace containing:

```text
skills/scientific-figure-design/v0.7.0.md
# or scientific-figure-design/v0.7.0.md
sciplib/plot_utils.py
scripts/lint_figure_code.py
config/active_skills.json
config/benchmark_config.yaml        # optional but preserved when present
skills/manifest.json                # optional but preserved when present
```

`config/active_skills.json` must declare:

```json
{
  "skills": {
    "scientific-figure-design": {
      "champion_version": "v0.7.0",
      "deterministic_modules": ["sciplib.plot_utils"],
      "static_linters": ["scripts/lint_figure_code.py"],
      "status": "production",
      "gate_no_regression": true
    }
  }
}
```

v0.6.5-opt is an archived previous baseline and must never be silently substituted for v0.7.0.

## Work / Codex run

Requires Node >=22.22 (Node 24 recommended), Python 3.11+, and either an existing Codex/ChatGPT login or `OPENAI_API_KEY`/`CODEX_API_KEY`.

From `skill-benchmark/`:

```bash
npm install
npm run fetch:tasks
npm run fetch:kdense
SCIENTIFIC_FIGURE_ROOT=/path/to/the/promoted/workspace npm run stage:v0.7
npm run preflight
npm run benchmark:full
```

Do not override `CODEX_HOME` when reusing an existing ChatGPT/Codex login unless the alternate home contains valid auth state.

## Controls

- Same Codex model and reasoning effort across all arms.
- Network and web search disabled during candidate execution.
- Unique filesystem for every task × replicate × arm.
- Deterministic artifact checks run before subjective scoring.
- The v0.7.0 AST linter is copied into the evaluator and applied uniformly to generated code from all three arms.
- Skill-use telemetry is diagnostic only; it cannot rescue a scientifically invalid artifact.
- No automatic champion promotion.

## Current phase

This branch contains the generation + deterministic-gate harness. Subjective scientific/visual judging must remain blinded to candidate identity and should reverse candidate presentation order before a winner claim is made.
