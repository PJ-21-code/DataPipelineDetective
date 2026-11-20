import os
import sys
import json
import time
from datetime import datetime

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from benchmarks.generate_datasets import main as generate_all_datasets
from benchmarks.benchmark_anomaly import run_anomaly_benchmarks
from benchmarks.benchmark_pipeline import run_performance_benchmarks
from benchmarks.benchmark_routing import run_routing_benchmarks
from benchmarks.benchmark_sql_remediation import run_sql_remediation_benchmarks
from benchmarks.benchmark_llm_diagnosis import run_llm_benchmarks

def run_all():
    start_time = time.time()
    print("=" * 80)
    print("🚀 DATA PIPELINE DETECTIVE - FULL BENCHMARKING SUITE")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)
    
    # Step 1: Generate datasets
    print("\n>>> STEP 1: Generating Reproducible Synthetic Datasets with Ground Truth...")
    generate_all_datasets()
    
    # Step 2: Anomaly Detection
    print("\n>>> STEP 2: Benchmarking Unsupervised Anomaly Detection (Isolation Forest)...")
    anomaly_res = run_anomaly_benchmarks()
    
    # Step 3: Pipeline Performance & Latency
    print("\n>>> STEP 3: Benchmarking Pipeline Latency, Throughput & Scaling (100, 1k, 10k)...")
    pipeline_res = run_performance_benchmarks()
    
    # Step 4: Conditional Routing
    print("\n>>> STEP 4: Benchmarking Conditional Routing & Branch Optimization...")
    routing_res = run_routing_benchmarks()
    
    # Step 5: SQL Remediation
    print("\n>>> STEP 5: Benchmarking SQL Remediation & Data Validation...")
    sql_res = run_sql_remediation_benchmarks()
    
    # Step 6: LLM Diagnosis
    print("\n>>> STEP 6: Benchmarking LLM Diagnostic Reasoning & Tool Performance...")
    llm_res = run_llm_benchmarks()
    
    total_duration = round(time.time() - start_time, 2)
    
    # Compile comprehensive final report object
    comprehensive_report = {
        "benchmark_timestamp": datetime.now().isoformat(),
        "total_suite_duration_seconds": total_duration,
        "environment": {
            "python_version": sys.version,
            "platform": sys.platform
        },
        "anomaly_detection": anomaly_res,
        "pipeline_performance": pipeline_res,
        "conditional_routing": routing_res,
        "sql_remediation": sql_res,
        "llm_diagnosis": llm_res
    }
    
    out_dir = os.path.dirname(os.path.abspath(__file__))
    summary_path = os.path.join(out_dir, "benchmark_summary.json")
    with open(summary_path, "w") as f:
        json.dump(comprehensive_report, f, indent=2)
        
    print("\n" + "=" * 80)
    print(f"✅ ALL BENCHMARKS COMPLETED in {total_duration}s")
    print(f"📊 Results compiled and saved to: {summary_path}")
    print("=" * 80)
    
    return comprehensive_report

if __name__ == "__main__":
    run_all()
