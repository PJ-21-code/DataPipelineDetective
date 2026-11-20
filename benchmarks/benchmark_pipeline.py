import os
import sys
import time
import json
import numpy as np
import pandas as pd

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from Agents.profiler import profiler_node
from Agents.anomaly import anomaly_node
from Agents.diagnostic import diagnostic_node
from Agents.sql_fix import sql_fix_node
from Agents.validation import validation_node
from Agents.contract import contract_node
from Agents.graph import build_graph

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def benchmark_individual_nodes(file_path, n_iterations=10):
    """Benchmark the execution latency of each individual pipeline node."""
    latencies = {
        "profiler": [],
        "anomaly": [],
        "sql_fix": [],
        "validation": [],
        "contract": []
    }
    
    # Pre-generate mock states to feed into downstream nodes accurately
    state = {"file_path": file_path}
    
    for _ in range(n_iterations):
        # Profiler
        t0 = time.perf_counter()
        prof_res = profiler_node(state)
        latencies["profiler"].append(time.perf_counter() - t0)
        
        # Anomaly
        t0 = time.perf_counter()
        anom_res = anomaly_node(state)
        latencies["anomaly"].append(time.perf_counter() - t0)
        
        # SQL Fix
        merged_state = {**state, **prof_res, **anom_res}
        t0 = time.perf_counter()
        sql_res = sql_fix_node(merged_state)
        latencies["sql_fix"].append(time.perf_counter() - t0)
        
        # Validation
        t0 = time.perf_counter()
        val_res = validation_node(merged_state)
        latencies["validation"].append(time.perf_counter() - t0)
        
        # Contract
        t0 = time.perf_counter()
        con_res = contract_node(merged_state)
        latencies["contract"].append(time.perf_counter() - t0)
        
    summary = {}
    for node, times in latencies.items():
        summary[node] = {
            "mean_ms": round(float(np.mean(times) * 1000), 2),
            "p50_ms": round(float(np.percentile(times, 50) * 1000), 2),
            "p95_ms": round(float(np.percentile(times, 95) * 1000), 2),
            "std_ms": round(float(np.std(times) * 1000), 2)
        }
    return summary

def benchmark_end_to_end_compute(graph, file_path, n_records, n_iterations=15):
    """
    Benchmark end-to-end LangGraph execution with deterministic/fallback diagnostic
    to measure raw data processing throughput and algorithmic scalability without network noise.
    """
    initial_state = {
        "file_path": file_path,
        "profile": {},
        "anomaly": {},
        "diagnosis": "",
        "has_issues": False,
        "database_fix": "",
        "validation": {},
        "data_contract": ""
    }
    
    # Warmup
    graph.invoke(initial_state)
    
    times = []
    for _ in range(n_iterations):
        t0 = time.perf_counter()
        graph.invoke(initial_state)
        times.append(time.perf_counter() - t0)
        
    times_arr = np.array(times)
    mean_s = float(np.mean(times_arr))
    p50_s = float(np.percentile(times_arr, 50))
    p95_s = float(np.percentile(times_arr, 95))
    throughput_rec_per_sec = n_records / mean_s if mean_s > 0 else 0.0
    
    return {
        "records": n_records,
        "iterations": n_iterations,
        "mean_latency_ms": round(mean_s * 1000, 2),
        "std_latency_ms": round(float(np.std(times_arr)) * 1000, 2),
        "p50_latency_ms": round(p50_s * 1000, 2),
        "p95_latency_ms": round(p95_s * 1000, 2),
        "min_latency_ms": round(float(np.min(times_arr)) * 1000, 2),
        "max_latency_ms": round(float(np.max(times_arr)) * 1000, 2),
        "throughput_records_per_sec": round(throughput_rec_per_sec, 1)
    }

def run_performance_benchmarks():
    print("=" * 70)
    print("⚡ PIPELINE PERFORMANCE & LATENCY BENCHMARK SUITE")
    print("=" * 70)
    
    graph = build_graph()
    sizes = [100, 1000, 10000]
    
    perf_results = {
        "end_to_end_compute": {},
        "node_breakdown": {}
    }
    
    for n in sizes:
        csv_file = os.path.join(DATA_DIR, f"perf_{n}.csv")
        print(f"\nBenchmarking dataset: {n} records ({csv_file})...")
        
        # End to end
        e2e = benchmark_end_to_end_compute(graph, csv_file, n, n_iterations=15)
        perf_results["end_to_end_compute"][n] = e2e
        print(f"  E2E Mean: {e2e['mean_latency_ms']} ms | P50: {e2e['p50_latency_ms']} ms | P95: {e2e['p95_latency_ms']} ms | Throughput: {e2e['throughput_records_per_sec']} rec/sec")
        
        # Node breakdown
        node_summary = benchmark_individual_nodes(csv_file, n_iterations=10)
        perf_results["node_breakdown"][n] = node_summary
        print("  Node Latencies (Mean ms): " + ", ".join([f"{k}: {v['mean_ms']}ms" for k, v in node_summary.items()]))
        
    return perf_results

if __name__ == "__main__":
    results = run_performance_benchmarks()
    out_file = os.path.join(os.path.dirname(__file__), "pipeline_benchmark_results.json")
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {out_file}")
