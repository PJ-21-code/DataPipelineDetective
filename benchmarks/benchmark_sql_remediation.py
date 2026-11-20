import os
import sys
import sqlite3
import json
import pandas as pd
import numpy as np

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from Agents.profiler import profiler_node
from Agents.sql_fix import sql_fix_node
from Agents.validation import validation_node

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
TEST_CASES_DIR = os.path.join(ROOT_DIR, "evaluation", "test_cases")

def test_sql_execution_in_sqlite(df, sql_query):
    """
    Executes the generated SQL query in an in-memory SQLite database
    to empirically verify syntactic validity and semantic execution.
    """
    conn = sqlite3.connect(":memory:")
    # Write dataframe to SQLite table raw_pipeline_data
    df.to_sql("raw_pipeline_data", conn, index=False, if_exists="replace")
    
    try:
        df_result = pd.read_sql_query(sql_query, conn)
        conn.close()
        
        # Check remaining duplicates and nulls in SQL result
        remaining_dupes = int(df_result.duplicated().sum())
        remaining_nulls = int(df_result.isnull().sum().sum())
        
        return {
            "sql_execution_status": "SUCCESS",
            "result_rows": len(df_result),
            "remaining_duplicates_in_sql": remaining_dupes,
            "remaining_nulls_in_sql": remaining_nulls,
            "error": None
        }
    except Exception as e:
        conn.close()
        return {
            "sql_execution_status": "FAILED",
            "result_rows": 0,
            "remaining_duplicates_in_sql": -1,
            "remaining_nulls_in_sql": -1,
            "error": str(e)
        }

def evaluate_remediation_on_file(file_path, file_name):
    df_raw = pd.read_csv(file_path)
    initial_rows = len(df_raw)
    initial_dupes = int(df_raw.duplicated().sum())
    initial_nulls = int(df_raw.isnull().sum().sum())
    total_detected_defects = initial_dupes + initial_nulls
    
    # 1. Run profiler
    state = {"file_path": file_path}
    profile_out = profiler_node(state)
    state.update(profile_out)
    
    # 2. Run SQL fix
    sql_out = sql_fix_node(state)
    state.update(sql_out)
    sql_query = sql_out.get("database_fix", "")
    
    # 3. Run validation node (built-in Pandas validation simulation)
    val_out = validation_node(state)
    state.update(val_out)
    val_data = val_out.get("validation", {})
    
    # 4. Run real SQL execution test in SQLite
    sql_test = test_sql_execution_in_sqlite(df_raw, sql_query)
    
    # 5. Calculate issue resolution percentage
    val_dupes_removed = val_data.get("duplicates_removed", 0)
    val_remaining_nulls = val_data.get("remaining_nulls", 0)
    val_nulls_fixed = initial_nulls - val_remaining_nulls
    
    defects_fixed = val_dupes_removed + val_nulls_fixed
    remediation_rate = (defects_fixed / total_detected_defects * 100) if total_detected_defects > 0 else 100.0
    
    return {
        "file_name": file_name,
        "initial_metrics": {
            "total_rows": initial_rows,
            "duplicates": initial_dupes,
            "null_values": initial_nulls,
            "total_defects": total_detected_defects
        },
        "generated_sql": sql_query,
        "sqlite_execution": sql_test,
        "validation_node_result": val_data,
        "resolution_metrics": {
            "duplicates_removed": val_dupes_removed,
            "nulls_fixed": val_nulls_fixed,
            "remaining_nulls": val_remaining_nulls,
            "remediation_success_rate": round(remediation_rate, 2),
            "fully_validated": val_data.get("status") == "SUCCESS" and val_remaining_nulls == 0
        }
    }

def run_sql_remediation_benchmarks():
    print("=" * 70)
    print("🛠️ SQL REMEDIATION & VALIDATION BENCHMARK SUITE")
    print("=" * 70)
    
    test_files = [
        ("remediation_duplicates.csv", os.path.join(DATA_DIR, "remediation_duplicates.csv")),
        ("remediation_nulls.csv", os.path.join(DATA_DIR, "remediation_nulls.csv")),
        ("remediation_mixed.csv", os.path.join(DATA_DIR, "remediation_mixed.csv")),
        ("corrupted_users.csv", os.path.join(TEST_CASES_DIR, "corrupted_users.csv")),
        ("enterprise_failure.csv", os.path.join(TEST_CASES_DIR, "enterprise_failure.csv"))
    ]
    
    all_results = []
    total_defects_across_tests = 0
    total_fixed_across_tests = 0
    sql_exec_success_count = 0
    
    for name, path in test_files:
        if not os.path.exists(path):
            print(f"Skipping {name}: file not found at {path}")
            continue
            
        res = evaluate_remediation_on_file(path, name)
        all_results.append(res)
        
        im = res["initial_metrics"]
        rm = res["resolution_metrics"]
        sq = res["sqlite_execution"]
        
        total_defects_across_tests += im["total_defects"]
        total_fixed_across_tests += (rm["duplicates_removed"] + rm["nulls_fixed"])
        if sq["sql_execution_status"] == "SUCCESS":
            sql_exec_success_count += 1
            
        print(f"\nTest: {name}")
        print(f"  Initial: {im['total_rows']} rows, {im['duplicates']} dupes, {im['null_values']} nulls (Total Defects: {im['total_defects']})")
        print(f"  SQL Execution in SQLite: {sq['sql_execution_status']} (Remaining Dupes: {sq['remaining_duplicates_in_sql']}, Nulls: {sq['remaining_nulls_in_sql']})")
        print(f"  Validation Status: {res['validation_node_result'].get('status')} | Success Rate: {rm['remediation_success_rate']}%")
        print(f"  Generated SQL Query:\n  {res['generated_sql'][:120]}...")
        
    overall_success_rate = (total_fixed_across_tests / total_defects_across_tests * 100) if total_defects_across_tests > 0 else 100.0
    sql_validity_rate = (sql_exec_success_count / len(test_files) * 100) if test_files else 0.0
    
    summary = {
        "tests_evaluated": len(all_results),
        "total_defects_tested": total_defects_across_tests,
        "total_defects_resolved": total_fixed_across_tests,
        "overall_remediation_success_rate": round(overall_success_rate, 2),
        "sqlite_execution_success_rate": round(sql_validity_rate, 2),
        "test_details": all_results
    }
    
    print("\n--- Summary ---")
    print(f"Total Defects Evaluated: {total_defects_across_tests}")
    print(f"Total Defects Resolved:  {total_fixed_across_tests}")
    print(f"Overall Remediation Rate: {overall_success_rate:.2f}%")
    print(f"SQL Syntax/Execution Success Rate: {sql_validity_rate:.1f}%")
    
    return summary

if __name__ == "__main__":
    res = run_sql_remediation_benchmarks()
    out_file = os.path.join(os.path.dirname(__file__), "sql_remediation_benchmark_results.json")
    with open(out_file, "w") as f:
        json.dump(res, f, indent=2)
    print(f"\nResults saved to {out_file}")
