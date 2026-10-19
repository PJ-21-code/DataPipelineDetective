from typing import TypedDict, Dict, Any

class PipelineState(TypedDict):
    file_path: str
    profile: Dict[str, Any]
    anomaly: Dict[str, Any]
    diagnosis: str          
    has_issues: bool         
    database_fix: str
    validation: Dict[str, Any]
    data_contract: str