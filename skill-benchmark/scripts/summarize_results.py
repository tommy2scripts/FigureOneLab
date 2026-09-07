#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, math, random, statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARMS = ["control", "scientific-v0.7", "kdense-v1.2"]
LABEL_TO_ARM = {"candidate-00": "control", "candidate-01": "scientific-v0.7", "candidate-02": "kdense-v1.2"}


def eval_rows(doc):
    block = doc.get("results", {})
    if isinstance(block, dict):
        rows = block.get("results") or block.get("outputs") or []
    else:
        rows = block
    return rows if isinstance(rows, list) else []


def label_from_result(r):
    text = json.dumps({k: r.get(k) for k in ("provider", "prompt", "response")}, default=str)
    return next((x for x in LABEL_TO_ARM if x in text), None)


def component_score(r, metric, default=None):
    comps = ((r.get("gradingResult") or {}).get("componentResults") or [])
    for c in comps:
        assertion = c.get("assertion") or {}
        if c.get("metric") == metric or assertion.get("metric") == metric:
            try: return float(c.get("score"))
            except Exception: return default
    return default


def response_output(r):
    return (r.get("response") or {}).get("output")


def bootstrap_ci(values, seed=20260906, n=10000):
    values = list(values)
    if not values: return [None, None]
    rng = random.Random(seed)
    means = []
    for _ in range(n):
        sample = [values[rng.randrange(len(values))] for _ in values]
        means.append(statistics.fmean(sample))
    means.sort()
    lo = means[int(0.025 * (n - 1))]
    hi = means[int(0.975 * (n - 1))]
    return [lo, hi]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--generation", default="artifacts/full-results.json")
    ap.add_argument("--judge", default="artifacts/judge-results.json")
    ap.add_argument("--mapping", default="artifacts/restricted_blind_map.json")
    ap.add_argument("--out", default="artifacts/summary.json")
    args = ap.parse_args()

    gen = json.loads((ROOT / args.generation).read_text())
    judge = json.loads((ROOT / args.judge).read_text())
    mapping = json.loads((ROOT / args.mapping).read_text())

    # Generation-level objective/operational evidence.
    g = {}
    for r in eval_rows(gen):
        label = label_from_result(r)
        if not label: continue
        arm = LABEL_TO_ARM[label]
        v = r.get("vars") or (r.get("testCase") or {}).get("vars") or {}
        try: key = (int(v["task_id"]), int(v["repeat_id"]), arm)
        except Exception: continue
        resp = r.get("response") or {}
        deterministic = component_score(r, "deterministic_contract", 1.0 if r.get("success") else 0.0)
        routing = component_score(r, "routing", None)
        if routing is None:
            calls = ((resp.get("metadata") or {}).get("skillCalls") or [])
            names = {x.get("name") for x in calls if isinstance(x, dict)}
            expected = {"control": None, "scientific-v0.7": "scientific-figure-design", "kdense-v1.2": "scientific-visualization"}[arm]
            routing = 1.0 if (not names if expected is None else expected in names) else 0.0
        g[key] = {
            "success": bool(r.get("success")),
            "deterministic": float(deterministic or 0),
            "routing": float(routing or 0),
            "latency_ms": float(r.get("latencyMs") or resp.get("latencyMs") or 0),
            "cost": float(resp.get("cost") or r.get("cost") or 0),
        }

    # Judge-level blinded scientific/visual evidence, averaged across reversed order.
    jacc = defaultdict(list)
    pref = defaultdict(dict)
    for r in eval_rows(judge):
        v = r.get("vars") or (r.get("testCase") or {}).get("vars") or {}
        case_id = v.get("case_id")
        if not case_id or case_id not in mapping: continue
        try: payload = json.loads(response_output(r))
        except Exception: continue
        parts = case_id.split("-")
        tid, rep, order = int(parts[1]), int(parts[3]), parts[4]
        m = mapping[case_id]
        for cand in ("candidate_1", "candidate_2", "candidate_3"):
            arm = m[cand]
            s = payload[cand]
            jacc[(tid, rep, arm)].append({
                "scientific": float(s["scientific_correctness"]) / 4 * 100,
                "requirements": float(s["task_requirements"]) / 4 * 100,
                "visual": float(s["visual_quality"]) / 4 * 100,
                "critical": bool(s["critical_error"]),
            })
        p = payload.get("pairwise_preference")
        pref[(tid, rep)][order] = "tie" if p == "tie" else m.get(p)

    rows = []
    for tid in range(1, 101):
        for rep in range(1, 4):
            # efficiency is normalized within the matched triplet; keep it low weight.
            lat = {a: max(g.get((tid, rep, a), {}).get("latency_ms", 0), 1) for a in ARMS}
            costs = {a: g.get((tid, rep, a), {}).get("cost", 0) for a in ARMS}
            min_lat = min(lat.values())
            positive_costs = [x for x in costs.values() if x > 0]
            min_cost = min(positive_costs) if positive_costs else 0
            for arm in ARMS:
                judges = jacc.get((tid, rep, arm), [])
                if judges:
                    sci = statistics.fmean(x["scientific"] for x in judges)
                    req = statistics.fmean(x["requirements"] for x in judges)
                    vis = statistics.fmean(x["visual"] for x in judges)
                    critical = any(x["critical"] for x in judges)
                else:
                    sci = req = vis = 0.0; critical = True
                gg = g.get((tid, rep, arm), {"success": False, "deterministic": 0, "routing": 0, "latency_ms": 0, "cost": 0})
                det = 100 * gg["deterministic"]
                route = 100 * gg["routing"]
                lat_score = min(100.0, 100 * min_lat / lat[arm])
                if min_cost and costs[arm] > 0:
                    cost_score = min(100.0, 100 * min_cost / costs[arm])
                    efficiency = (lat_score + cost_score) / 2
                else:
                    efficiency = lat_score
                gate = bool(gg["success"] and gg["deterministic"] >= 1 and not critical)
                composite = (0.35*sci + 0.25*req + 0.20*det + 0.15*vis + 0.03*route + 0.02*efficiency) if gate else None
                rows.append({
                    "task_id": tid, "repeat_id": rep, "arm": arm, "gate_pass": gate,
                    "scientific": sci, "requirements": req, "deterministic": det, "visual": vis,
                    "routing": route, "efficiency": efficiency, "composite": composite,
                    "critical_error": critical, "latency_ms": gg["latency_ms"], "cost": gg["cost"],
                })

    # Aggregate replicates within task before any across-task inference.
    task_scores = defaultdict(dict)
    for tid in range(1, 101):
        for arm in ARMS:
            rr = [x for x in rows if x["task_id"] == tid and x["arm"] == arm]
            vals = [x["composite"] for x in rr if x["composite"] is not None]
            task_scores[tid][arm] = statistics.fmean(vals) if vals else None

    def deltas(a, b):
        out = []
        for tid in range(1, 101):
            x, y = task_scores[tid][a], task_scores[tid][b]
            if x is not None and y is not None: out.append(x-y)
        return out

    ab = deltas("scientific-v0.7", "kdense-v1.2")
    ac = deltas("scientific-v0.7", "control")
    bc = deltas("kdense-v1.2", "control")
    preference_inconsistent = 0
    preference_total = 0
    pair_wtl = {"scientific-v0.7": 0, "kdense-v1.2": 0, "tie": 0}
    for key, orders in pref.items():
        if "ab" not in orders or "ba" not in orders: continue
        preference_total += 1
        if orders["ab"] != orders["ba"]:
            preference_inconsistent += 1
        if orders["ab"] == orders["ba"]:
            pair_wtl[orders["ab"]] = pair_wtl.get(orders["ab"], 0) + 1
        else:
            pair_wtl["tie"] += 1

    arm_summary = {}
    for arm in ARMS:
        rr = [x for x in rows if x["arm"] == arm]
        valid = [x["composite"] for x in rr if x["composite"] is not None]
        task_valid = [task_scores[t][arm] for t in range(1,101) if task_scores[t][arm] is not None]
        arm_summary[arm] = {
            "replicate_gate_pass_rate": sum(x["gate_pass"] for x in rr) / len(rr),
            "catastrophic_failure_rate": sum(x["critical_error"] or not x["gate_pass"] for x in rr) / len(rr),
            "valid_task_count": len(task_valid),
            "task_mean_composite": statistics.fmean(task_valid) if task_valid else None,
            "task_median_composite": statistics.median(task_valid) if task_valid else None,
            "total_cost": sum(x["cost"] for x in rr),
            "median_latency_ms": statistics.median([x["latency_ms"] for x in rr if x["latency_ms"] > 0]) if any(x["latency_ms"] > 0 for x in rr) else None,
        }

    def comp(name, vals):
        return {
            "comparison": name,
            "paired_task_count": len(vals),
            "mean_delta": statistics.fmean(vals) if vals else None,
            "median_delta": statistics.median(vals) if vals else None,
            "bootstrap_95_ci": bootstrap_ci(vals),
            "wins": sum(x > 0 for x in vals), "ties": sum(x == 0 for x in vals), "losses": sum(x < 0 for x in vals),
        }

    summary = {
        "design": {"tasks": 100, "replicates": 3, "generation_executions": 900, "judge_executions": 600},
        "weights": {"scientific": .35, "requirements": .25, "deterministic": .20, "visual": .15, "routing": .03, "efficiency": .02},
        "arms": arm_summary,
        "comparisons": [
            comp("scientific-v0.7 minus kdense-v1.2", ab),
            comp("scientific-v0.7 minus control", ac),
            comp("kdense-v1.2 minus control", bc),
        ],
        "reversed_order_pairwise": {
            "cases_with_both_orders": preference_total,
            "position_inconsistent": preference_inconsistent,
            "position_inconsistency_rate": preference_inconsistent/preference_total if preference_total else None,
            "resolved_win_tie_loss": pair_wtl,
        },
    }
    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
