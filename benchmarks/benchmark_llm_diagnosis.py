import os
import sys
import time
import json
import numpy as np

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from Agents.profiler import profiler_node
from Agents.anomaly import anomaly_node
from Agents.diagnostic import diagnostic_node

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
TEST_CASES_DIR = os.path.join(ROOT_DIR, "evaluation", "test_cases")

def score_diagnosis_content(diagnosis_text, ground_truth):
    """
    Evaluates whether the LLM diagnosis correctly identifies the specific
    root causes and impact areas known to be present in the data.
    """
    text_lower = diagnosis_text.lower()
    
    # 1. Structural adherence
    has_root_cause_section = "root" in text_lower and "cause" in text_lower
    has_impact_section = "impact" in text_lower or "business" in text_lower or "analytics" in text_lower
    
    # 2. Defect recognition accuracy
    identified_dupes = ("duplicate" in text_lower or "deduplication" in text_lower) if ground_truth["has_dupes"] else True
    identified_nulls = ("null" in text_lower or "missing" in text_lower or "omission" in text_lower) if ground_truth["has_nulls"] else True
    identified_anomalies = ("anomal" in text_lower or "outlier" in text_lower or "drift" in text_lower) if ground_truth["has_anomalies"] else True
    
    # 3. Clean pipeline detection (if healthy, did it recognize it)
    clean_recognized = ("healthy" in text_lower or "pristine" in text_lower or "no anomalies" in text_lower) if ground_truth.get("is_clean", False) else True
    
    checks = {
        "has_root_cause_section": has_root_cause_section,
        "has_impact_section": has_impact_section,
        "identified_duplicates": identified_dupes,
        "identified_nulls": identified_nulls,
        "identified_anomalies": identified_anomalies,
        "clean_recognized": clean_recognized
    }
    
    score = sum(1 for v in checks.values() if v) / len(checks)
    return checks, score

def evaluate_diagnostic_case(file_path, case_name, ground_truth):
    state = {"file_path": file_path}
    
    # Run upstream profiler & anomaly nodes
    prof = profiler_node(state)
    state.update(prof)
    anom = anomaly_node(state)
    state.update(anom)
    
    # Time LLM invocation
    t0 = time.perf_counter()
    diag_out = diagnostic_node(state)
    latency_s = time.perf_counter() - t0
    
    diagnosis_text = diag_out.get("diagnosis", "")
    has_issues = diag_out.get("has_issues", False)
    
    # Check tool success & state integrity
    state_valid = isinstance(diag_out, dict) and "diagnosis" in diag_out and "has_issues" in diag_out
    is_fallback = "Fallback Diagnosis" in diagnosis_text
    
    checks, acc_score = score_diagnosis_content(diagnosis_text, ground_truth)
    
    return {
        "case_name": case_name,
        "latency_ms": round(latency_s * 1000, 2),
        "state_schema_valid": state_valid,
        "is_fallback": is_fallback,
        "has_issues_flag": has_issues,
        "diagnosis_length_chars": len(diagnosis_text),
        "evaluation_checks": checks,
        "accuracy_score": round(acc_score, 4),
        "diagnosis_preview": diagnosis_text[:250] + "..." if len(diagnosis_text) > 250 else diagnosis_text
    }

def run_llm_benchmarks():
    print("=" * 70)
    print("🧠 LLM DIAGNOSIS BENCHMARK SUITE (Groq Llama 3 / GPT-OSS)")
    print("=" * 70)
    
    test_cases = [
        {
            "name": "enterprise_failure.csv",
            "path": os.path.join(TEST_CASES_DIR, "enterprise_failure.csv"),
            "ground_truth": {"has_dupes": True, "has_nulls": True, "has_anomalies": True, "is_clean": False}
        },
        {
            "name": "corrupted_users.csv",
            "path": os.path.join(TEST_CASES_DIR, "corrupted_users.csv"),
            "ground_truth": {"has_dupes": True, "has_nulls": True, "has_anomalies": True, "is_clean": False}
        },
        {
            "name": "remediation_duplicates.csv",
            "path": os.path.join(DATA_DIR, "remediation_duplicates.csv"),
            "ground_truth": {"has_dupes": True, "has_nulls": False, "has_anomalies": False, "is_clean": False}
        },
        {
            "name": "remediation_nulls.csv",
            "path": os.path.join(DATA_DIR, "remediation_nulls.csv"),
            "ground_truth": {"has_dupes": False, "has_nulls": True, "has_anomalies": False, "is_clean": False}
        },
        {
            "name": "routing_clean.csv",
            "path": os.path.join(DATA_DIR, "routing_clean.csv"),
            "ground_truth": {"has_dupes": False, "has_nulls": False, "has_anomalies": False, "is_clean": True}
        }
    ]
    
    results = []
    latencies = []
    scores = []
    valid_states = 0
    fallback_count = 0
    
    for tc in test_cases:
        if not os.path.exists(tc["path"]):
            continue
            
        print(f"\nEvaluating Case: {tc['name']}...")
        res = evaluate_diagnostic_case(tc["path"], tc["name"], tc["ground_truth"])
        results.append(res)
        
        latencies.append(res["latency_ms"])
        scores.append(res["accuracy_score"])
        if res["state_schema_valid"]:
            valid_states += 1
        if res["is_fallback"]:
            fallback_count += 1
            
        print(f"  Latency: {res['latency_ms']} ms | Fallback: {res['is_fallback']} | Accuracy Score: {res['accuracy_score']*100:.1f}%")
        print(f"  Diagnosis: {res['diagnosis_preview'][:100]}...")
        
    lat_arr = np.array(latencies)
    summary = {
        "cases_evaluated": len(results),
        "tool_state_success_rate": round((valid_states / len(results)) * 100, 2),
        "fallback_rate": round((fallback_count / len(results)) * 100, 2),
        "mean_accuracy": round(float(np.mean(scores)) * 100, 2),
        "latency_metrics": {
            "mean_ms": round(float(np.mean(lat_arr)), 2),
            "p50_ms": round(float(np.percentile(lat_arr, 50)), 2),
            "p95_ms": round(float(np.percentile(lat_arr, 95)), 2),
            "min_ms": round(float(np.min(lat_arr)), 2),
            "max_ms": round(float(np.max(lat_arr)), 2)
        },
        "case_details": results
    }
    
    print("\n--- LLM Benchmark Summary ---")
    print(f"State Schema Integrity: {summary['tool_state_success_rate']}%")
    print(f"Mean Diagnostic Accuracy: {summary['mean_accuracy']}%")
    print(f"Latency P50: {summary['latency_metrics']['p50_ms']} ms | P95: {summary['latency_metrics']['p95_ms']} ms | Mean: {summary['latency_metrics']['mean_ms']} ms")
    
    return summary

if __name__ == "__main__":
    res = run_llm_benchmarks()
    out_file = os.path.join(os.path.dirname(__file__), "llm_benchmark_results.json")
    with open(out_file, "w") as f:
        json.dump(res, f, indent=2)
    print(f"\nResults saved to {out_file}")
