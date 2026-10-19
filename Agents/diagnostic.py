import os
from typing import Dict, Any
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
from Agents.state import PipelineState

load_dotenv()

def diagnostic_node(state: PipelineState) -> Dict[str, Any]:
    """
    Diagnostic Reasoning Agent: Uses Groq (Llama 3) to synthesize root cause and business impact.
    """
    profile = state.get("profile", {})
    anomaly = state.get("anomaly", {})
    
    # Determine if data has any actionable issues
    duplicate_rows = profile.get("duplicate_rows", 0)
    null_counts = profile.get("null_counts", {})
    anomaly_count = anomaly.get("anomaly_count", 0)
    
    has_issues = duplicate_rows > 0 or bool(null_counts) or anomaly_count > 0
    
    if not has_issues:
        return {
            "diagnosis": "✅ **Pipeline Healthy**: No anomalies, null spikes, or duplicates detected. Data is pristine.",
            "has_issues": False
        }

    # Construct prompt for the LLM
    prompt = f"""
    You are an expert Data Pipeline Detective and Chief Data Officer. 
    Analyze the following data quality scan results and provide a structured diagnosis:
    
    1. **Root-Cause Diagnosis**: Explain precisely what likely caused this pipeline issue.
    2. **Downstream Business Impact**: Estimate how these defects distort analytics dashboards, metrics, or downstream models.

    Scan Results:
    - Total Rows: {profile.get('row_count')}
    - Duplicate Rows: {duplicate_rows}
    - Null Counts per Column: {null_counts}
    - ML Anomalies Detected: {anomaly_count}

    Keep your tone professional, concise, and engineering-focused. Use markdown formatting.
    """

    try:

        api_key= os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY is missing from environment variables or .env file.")
        
        llm = ChatGroq(api_key=api_key,model="openai/gpt-oss-20b", temperature=0.2)
        response = llm.invoke([HumanMessage(content=prompt)])
        diagnosis_text = response.content
    except Exception as e:
        # Fallback if API key is missing or invalid
        diagnosis_text = (
            f"⚠️ **Groq Fallback Diagnosis**:\n"
            f"- Found {duplicate_rows} duplicate rows.\n"
            f"- Detected null counts in columns: {list(null_counts.keys())}.\n"
            f"- Found {anomaly_count} ML anomalies.\n"
            f"(Groq API Error: {str(e)})"
        )

    return {
        "diagnosis": diagnosis_text,
        "has_issues": True
    }