import os
import sys
import glob
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Agents.graph import build_graph

def run_evaluation():
    print("🚀 Starting Data Pipeline Detective Evaluation Suite...\n")
    
    # Compile graph
    pipeline_graph = build_graph()
    
    # Locate all test case CSVs
    test_cases_dir = os.path.join(os.path.dirname(__file__), 'test_cases')
    csv_files = glob.glob(os.path.join(test_cases_dir, '*.csv'))
    
    if not csv_files:
        print(f"❌ No test CSV files found in {test_cases_dir}. Please add sample test files.")
        return

    results = []

    for file_path in csv_files:
        filename = os.path.basename(file_path)
        print(f"📂 Evaluating test case: {filename}...")

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

        try:
            # Run LangGraph workflow
            final_state = pipeline_graph.invoke(initial_state)
            
            # Extract metrics
            profile = final_state.get("profile", {})
            validation = final_state.get("validation", {})
            has_issues = final_state.get("has_issues", False)
            anomaly_count = final_state.get("anomaly", {}).get("anomaly_count", 0)
            
            results.append({
                "file": filename,
                "total_rows": profile.get("row_count", 0),
                "duplicates": profile.get("duplicate_rows", 0),
                "anomalies" : anomaly_count,
                "issues_detected": has_issues,
                "validation_status": validation.get("status", "SKIPPED")
            })
            print(f"   [SUCCESS] Pipeline executed successfully for {filename}.\n")
            
        except Exception as e:
            print(f"   [FAILED] Error processing {filename}: {str(e)}\n")

    # Print summary report table
    print("=" * 60)
    print("📊 EVALUATION SUMMARY REPORT")
    print("=" * 60)
    df_report = pd.DataFrame(results)
    print(df_report.to_string(index=False))
    print("=" * 60)

if __name__ == "__main__":
    run_evaluation()