from typing import TypedDict, Dict, Any

class PipelineState(TypedDict):
    file_path: str
    profile: Dict[str, Any]
    anomaly: Dict[str, Any]
    root_cause: str
    downstream_impact: str
    database_fix: str
    validation: Dict[str,Any]
    data_contract: str