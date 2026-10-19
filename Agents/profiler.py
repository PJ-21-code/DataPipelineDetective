import pandas as pd
from typing import Dict,Any
from Agents.state import PipelineState

def profiler_node(state: PipelineState) -> Dict[str, Any]:
    """
    Profiler Agent: Inspects schemas, nulls, duplicates, and distributions.
    """
    file_path = state["file_path"]
    
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        return {"profile": {"error": f"Failed to read CSV file: {str(e)}"}}

    # Extract data quality metrics
    row_count = len(df)
    duplicate_rows = int(df.duplicated().sum())
    null_counts = df.isnull().sum().to_dict()
    dtypes = {col: str(dtype) for col, dtype in df.dtypes.items()}
    
    # Safe numerical summary description
    numeric_summary = {}
    if not df.select_dtypes(include=['number']).empty:
        numeric_summary = df.describe().to_dict()

    profile_data = {
        "row_count": row_count,
        "duplicate_rows": duplicate_rows,
        "null_counts": null_counts,
        "dtypes": dtypes,
        "numeric_summary": numeric_summary
    }

    # Returns the update to merge back into the LangGraph state
    return {"profile": profile_data}