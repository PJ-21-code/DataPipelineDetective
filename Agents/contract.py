import pandas as pd
from typing import Dict, Any
from Agents.state import PipelineState

def contract_node(state: PipelineState) -> Dict[str, Any]:
    """
    Data Contract Agent: Generates a Pydantic validation schema snippet based on clean data columns and types.
    """
    file_path = state["file_path"]
    
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        return {"data_contract": f"# Error generating contract: {str(e)}"}

    # Map pandas dtypes to Python/Pydantic types
    type_mapping = {
        'int64': 'int',
        'float64': 'float',
        'object': 'str',
        'bool': 'bool',
        'datetime64[ns]': 'datetime'
    }

    fields = []
    for col, dtype in df.dtypes.items():
        py_type = type_mapping.get(str(dtype), 'str')
        # If there are missing values, make it Optional
        if df[col].isnull().any():
            py_type = f"Optional[{py_type}]"
        fields.append(f"    {col}: {py_type}")

    fields_str = "\n".join(fields)

    # Generate a clean Pydantic code snippet
    contract_code = (
        f"from pydantic import BaseModel\n"
        f"from typing import Optional\n"
        f"from datetime import datetime\n\n"
        f"class IngestionDataContract(BaseModel):\n"
        f"{fields_str}\n\n"
        f"    class Config:\n"
        f"        extra = 'forbid'  # Blocks upstream schema drift"
    )

    return {"data_contract": contract_code}