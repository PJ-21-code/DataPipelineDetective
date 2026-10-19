from typing import Dict, Any
from Agents.state import PipelineState

def sql_fix_node(state: PipelineState) -> Dict[str, Any]:
    """
    SQL Fix Agent: Proposes a corrective SQL query based on the data issues.
    """
    profile = state.get("profile", {})
    duplicate_rows = profile.get("duplicate_rows", 0)
    null_counts = profile.get("null_counts", {})
    
    # Build a sample corrective SQL query
    columns = list(profile.get("dtypes", {}).keys())
    
    if not columns:
        select_clause = "*"
    else:
        # Handle nulls with COALESCE for safety
        fixed_cols = []
        for col in columns:
            if null_counts.get(col, 0) > 0:
                fixed_cols.append(f"COALESCE({col}, 'DEFAULT_VALUE') AS {col}")
            else:
                fixed_cols.append(col)
        select_clause = ", ".join(fixed_cols)

    # Base query
    sql = f"SELECT {select_clause} FROM raw_pipeline_data"

    # If duplicates exist, add a deduplication CTE using Window Functions
    if duplicate_rows > 0:
        # Assume an 'id' or primary key exists, or use a general partition
        partition_col = columns[0] if columns else "id"
        sql = (
            f"WITH ranked_data AS (\n"
            f"    SELECT *,\n"
            f"           ROW_NUMBER() OVER(PARTITION BY {partition_col} ORDER BY (SELECT NULL)) as rn\n"
            f"    FROM raw_pipeline_data\n"
            f")\n"
            f"SELECT {select_clause}\n"
            f"FROM ranked_data\n"
            f"WHERE rn = 1;"
        )
    else:
        sql += ";"

    # Returns the update to merge back into the LangGraph state
    return {"database_fix": sql}