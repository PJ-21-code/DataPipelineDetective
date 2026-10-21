import os
import sys
import glob
import pandas as pd

# Add root directory to path so we can import from Agents/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Agents.graph import build_graph

def run_evaluation():
    print("🚀 Starting Data Pipeline Detective Deep Evaluation Suite...\n")
    
    # Compile graph
    pipeline_graph = build_graph()
    
    # Locate all test case CSVs
    test_cases_dir = os.path.join(os.path.dirname(__file__), 'test_cases')
    csv_files = glob.glob(os.path.join(test_cases_dir, '*.csv'))
    
    if not csv_files:
        print(f"❌ No test CSV files found in {test_cases_dir}. Please add sample test files.")
        return

    for file_path in csv_files:
        filename = os.path.basename(file_path)
        print("=" * 70)
        print(f"📂 TEST CASE FILE: {filename}")
        print("=" * 70)

        # Inspect raw file locally to display specific bad rows
        try:
            df = pd.read_csv(file_path)
            
            # Find duplicate rows
            duplicates = df[df.duplicated(keep=False)]
            
            # Find rows with missing (null) values
            null_rows = df[df.isnull().any(axis=1)]
            
            print(f"• Total Rows in File: {len(df)}")
            print(f"• Duplicate Rows Count: {len(duplicates)}")
            if not duplicates.empty:
                print("   ↳ Duplicate Entries Found:")
                print(duplicates.to_string(index=True))
                print()

            print(f"• Rows with Missing (Null) Values: {len(null_rows)}")
            if not null_rows.empty:
                print("   ↳ Null-Containing Entries Found:")
                print(null_rows.to_string(index=True))
                print()

        except Exception as read_err:
            print(f"⚠️ Could not pre-read local CSV: {read_err}")

        # Initial LangGraph state
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
            print("🤖 Running Groq Agent Team Pipeline...")
            final_state = pipeline_graph.invoke(initial_state)
            
            print("\n🧠 Groq LLM Diagnostic & Impact Report:")
            print("-" * 50)
            print(final_state.get("diagnosis", "No diagnosis generated."))
            print("-" * 50)
            
            print(f"✅ Validation Status: {final_state.get('validation', {}).get('status', 'SKIPPED')}\n")
            
        except Exception as e:
            print(f"❌ Pipeline Error on {filename}: {str(e)}\n")

    print("=" * 70)
    print("🎉 Evaluation Complete!")
    print("=" * 70)

if __name__ == "__main__":
    run_evaluation()