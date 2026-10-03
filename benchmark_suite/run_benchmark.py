"""
Vigyan AI: Benchmark Evaluation Runner
Evaluates STEM reasoning, exact calculus, and physical causal recall.
"""

import os
import sys
import json
import time
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core.agent import VigyanAgent

def score_response(item: dict, response: str, latency: float) -> dict:
    gt = item["ground_truth"]
    is_math = item["math"]
    score = 10.0
    fb = []

    if is_math:
        matched = False
        if gt.lower() in response.lower():
            matched = True
        else:
            try:
                num_pred = float(''.join(c for c in response if c.isdigit() or c == '.'))
                num_gt = float(gt)
                if abs(num_pred - num_gt) / (abs(num_gt) + 1e-9) < 0.05:
                    matched = True
            except Exception:
                pass
        if matched:
            fb.append("Exact Symbolic/Numeric Match")
        else:
            score -= 5.0
            fb.append(f"Math deviation (Expected: '{gt}')")
    else:
        gt_words = [w for w in gt.split() if len(w) > 3 and w.isalnum()]
        hits = sum(1 for w in gt_words if w.lower() in response.lower())
        recall = hits / max(1, len(gt_words))
        if recall < 0.35:
            score -= 4.0
            fb.append(f"Factual recall low ({recall*100:.0f}%)")
        else:
            fb.append(f"Factual recall adequate ({recall*100:.0f}%)")

    final_s = max(1.0, min(10.0, round(score, 1)))
    return {"score": final_s, "pass": final_s >= 6.5, "feedback": "; ".join(fb)}


def run_benchmark(tier: str = "7b", samples: int = 50, output_file: str = "benchmark_report.json"):
    print("=" * 75)
    print("🚀 VIGYAN AI: NEURO-SYMBOLIC STEM BENCHMARK EVALUATOR")
    print(f"Target Model Tier: {tier.upper()}")
    print("Engine Grounding : SymPy C-Python AST + KùzuDB C++ GraphRAG")
    print("=" * 75)

    cases_path = os.path.join(os.path.dirname(__file__), "test_cases.json")
    with open(cases_path, "r") as f:
        all_cases = json.load(f)
    cases = all_cases[:samples]

    agent = VigyanAgent(model_tier=tier)

    results = []
    total_time = 0
    passed_count = 0

    for idx, item in enumerate(cases, 1):
        q = item["query"]
        dom = item["domain"]
        t0 = time.time()
        ans = agent.answer(q)
        lat = round(time.time() - t0, 4)
        total_time += lat

        resp = ans.get("response", "")
        eval_res = score_response(item, resp, lat)
        if eval_res["pass"]:
            passed_count += 1

        print(f"[{idx}/{len(cases)}] [{dom}] {q[:45]}... -> Score: {eval_res['score']}/10 ({lat:.4f}s)")

        results.append({
            "id": item["id"],
            "domain": dom,
            "query": q,
            "latency_s": lat,
            "score": eval_res["score"],
            "passed": eval_res["pass"],
            "intent": ans.get("intent"),
            "tool_used": ans.get("tool_used"),
            "feedback": eval_res["feedback"]
        })

    avg_lat = total_time / len(cases)
    acc = (passed_count / len(cases)) * 100.0

    print("\n" + "=" * 75)
    print("📊 BENCHMARK SUMMARY SCOREBOARD")
    print("=" * 75)
    print(f"Total Cases Evaluated   : {len(cases)}")
    print(f"Passed Cases            : {passed_count}/{len(cases)}")
    print(f"Accuracy Rate           : {acc:.1f}%")
    print(f"Average Turn Latency    : {avg_lat:.4f}s")
    print("=" * 75)

    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "tier": tier,
        "total_cases": len(cases),
        "passed": passed_count,
        "accuracy_pct": round(acc, 1),
        "avg_latency_s": round(avg_lat, 4),
        "details": results
    }

    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Audit log saved to: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tier", type=str, default="7b", choices=["2b", "7b", "32b"])
    parser.add_argument("--samples", type=int, default=50)
    parser.add_argument("--output", type=str, default="benchmark_report.json")
    args = parser.parse_args()
    run_benchmark(args.tier, args.samples, args.output)
