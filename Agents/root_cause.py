import pandas as pd
from typing import Dict,Any
from Agents.state import PipelineState

def root_cause_node(state: PipelineState) -> Dict[str, Any]:
    """
    Root-Cause Agent: Investigates likely failure points based on profile and anomaly data.
    """
    profile = state.get("profile", {})
    anomaly = state.get("anomaly", {})
    
    issues = []
    
    # Check for duplicate rows
    duplicate_rows = profile.get("duplicate_rows", 0)
    if duplicate_rows > 0:
        issues.append(f"Found {duplicate_rows} duplicate rows, indicating missing deduplication steps during ingestion.")
        
    # Check for excessive missing values / nulls
    null_counts = profile.get("null_counts", {})
    row_count = profile.get("row_count", 1)
    for col, nulls in null_counts.items():
        if nulls > 0:
            pct = (nulls / row_count) * 100
            if pct > 20:
                issues.append(f"Column '{col}' has {pct:.1f}% missing values, signaling upstream schema drift or null-injection.")
                
    # Check for machine learning anomalies
    anomaly_count = anomaly.get("anomaly_count", 0)
    if anomaly_count > 0:
        msg = anomaly.get("message", f"Detected {anomaly_count} statistical anomalies.")
        issues.append(msg)
        
    if not issues:
        root_cause_text = "No critical root-cause anomalies detected. The data pipeline appears healthy."
    else:
        root_cause_text = " ".join(issues)

    # Returns the update to merge back into the LangGraph state
    return {"root_cause": root_cause_text}