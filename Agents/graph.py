from langgraph.graph import StateGraph, START, END

from Agents.profiler import profiler_node
from Agents.anomaly import anomaly_node
from Agents.diagnostic import diagnostic_node
from Agents.sql_fix import sql_fix_node
from Agents.validation import validation_node
from Agents.contract import contract_node
from Agents.state import PipelineState

def route_after_diagnostic(state: PipelineState) -> str:
    """Conditional router based on whether issues were found."""
    if state.get("has_issues", False):
        return "sql_fix_node"
    else:
        return "contract_node"

def build_graph():
    workflow= StateGraph(PipelineState)

    workflow.add_node("profiler_node", profiler_node)
    workflow.add_node("anomaly_node",anomaly_node)
    workflow.add_node("diagnostic_node",diagnostic_node)
    workflow.add_node("sql_fix_node",sql_fix_node)
    workflow.add_node("validation_node",validation_node)
    workflow.add_node("contract_node",contract_node)

    workflow.add_edge(START,"profiler_node")
    workflow.add_edge("profiler_node","anomaly_node")
    workflow.add_edge("anomaly_node","diagnostic_node")

    workflow.add_conditional_edges(
        "diagnostic_node",
        route_after_diagnostic,
        {
            "sql_fix_node": "sql_fix_node",
            "contract_node": "contract_node"
        }
    )
    
    workflow.add_edge("sql_fix_node","validation_node")
    workflow.add_edge("validation_node","contract_node")
    workflow.add_edge("contract_node", END)

    chain= workflow.compile()

    return chain


