import pandas as pd
from sklearn.ensemble import IsolationForest
from typing import Dict,Any
from Agents.state import PipelineState

def anomaly_node(state: PipelineState) -> Dict[str, Any]:
    """
    Anomaly Agent: Detects suspicious changes or outliers using Isolation Forest.
    """
    file_path = state["file_path"]
    
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        return {"anomaly": {"error": f"Failed to read CSV file: {str(e)}"}}

    # Select numeric columns for machine learning anomaly detection
    df_numeric = df.select_dtypes(include=['number']).dropna()
    
    if df_numeric.empty or len(df_numeric) < 5:
        return {
            "anomaly": {
                "anomaly_count": 0, 
                "percentage": 0.0,
                "message": "Not enough numeric data for ML anomaly detection."
            }
        }

    # Run Isolation Forest
    iso = IsolationForest(contamination=0.05, random_state=42)
    preds = iso.fit_predict(df_numeric)
    anomaly_count = int((preds == -1).sum())
    percentage = round((anomaly_count / len(df_numeric)) * 100, 2)

    anomaly_data = {
        "anomaly_count": anomaly_count,
        "percentage": percentage,
        "message": f"Detected {anomaly_count} statistical outliers ({percentage}% of dataset)."
    }

    # Returns the update to merge back into the LangGraph state
    return {"anomaly": anomaly_data}