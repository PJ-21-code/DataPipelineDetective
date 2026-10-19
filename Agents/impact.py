import pandas as pd
from typing import Dict, Any
from Agents.state import PipelineState

def impact_node(state: PipelineState) -> Dict[str, Any]:
    """
    Downstream Impact Agent: Translates technical data anomalies into estimated business and analytics impact.
    """
    profile = state.get("profile", {})
    anomaly = state.get("anomaly", {})
    
    row_count = profile.get("row_count", 1)
    duplicate_rows = profile.get("duplicate_rows", 0)
    null_counts = profile.get("null_counts", {})
    anomaly_count = anomaly.get("anomaly_count", 0)
    
    impact_statements = []
    
    # 1. Duplicate impact analysis
    if duplicate_rows > 0:
        dup_pct = round((duplicate_rows / row_count) * 100, 2)
        impact_statements.append(
            f"• **Analytics Distortion**: {duplicate_rows} duplicate rows ({dup_pct}% of dataset) detected. "
            f"Downstream reporting and user-metric dashboards will likely overreport volume or revenue metrics proportionally."
        )
        
    # 2. Missing data impact analysis
    high_null_cols = [col for col, nulls in null_counts.items() if (nulls / row_count) * 100 > 15]
    if high_null_cols:
        impact_statements.append(
            f"• **Data Completeness Risk**: Critical columns ({', '.join(high_null_cols)}) suffer from high null rates. "
            f"Machine learning features relying on these attributes will experience prediction drop-offs or default-value skew."
        )
        
    # 3. Anomaly impact analysis
    if anomaly_count > 0:
        anomaly_pct = anomaly.get("percentage", 0.0)
        impact_statements.append(
            f"• **Financial / Operational Risk**: {anomaly_count} statistical anomalies ({anomaly_pct}% of records) found. "
            f"Unfiltered outliers risk breaking automated billing triggers or corrupting sliding-window aggregations."
        )

    if not impact_statements:
        impact_summary = "No significant downstream business impact detected. Data health is optimal."
    else:
        impact_summary = "\n".join(impact_statements)

    return {"downstream_impact": impact_summary}