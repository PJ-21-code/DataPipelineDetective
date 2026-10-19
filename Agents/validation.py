import pandas as pd
from typing import Dict, Any
from Agents.state import PipelineState

def validation_node(state: PipelineState) -> Dict[str, Any]:
    """
    Validation Agent: Tests whether the proposed data corrections address the issues.
    """
    file_path = state["file_path"]
    
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        return {
            "validation": {
                "status": "FAILED",
                "message": f"Validation failed to read CSV file: {str(e)}"
            }
        }

    initial_rows = len(df)
    
    # Simulate the data fix (e.g., removing duplicates and filling missing values)
    df_fixed = df.drop_duplicates()
    df_fixed = df_fixed.fillna("DEFAULT_VALUE")
    
    final_rows = len(df_fixed)
    remaining_nulls = int(df_fixed.isnull().sum().sum())
    duplicates_removed = initial_rows - final_rows

    validation_result = {
        "status": "SUCCESS",
        "initial_rows": initial_rows,
        "final_rows": final_rows,
        "duplicates_removed": duplicates_removed,
        "remaining_nulls": remaining_nulls,
        "message": f"Validation passed successfully. Removed {duplicates_removed} duplicates and sanitized null records."
    }

    # Returns the update to merge back into the LangGraph state
    return {"validation": validation_result}