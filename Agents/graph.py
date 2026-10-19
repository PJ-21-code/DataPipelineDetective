from langgraph.graph import StateGraph, START, END

from Agents.profiler import profiler_node
from Agents.anomaly import anomaly_node
from Agents.root_cause import root_cause_node
from Agents.impact import impact_node
from Agents.sql_fix import sql_fix_node
from Agents.validation import validation_node
from Agents.contract import contract_node
from Agents.state import PipelineState

def build_graph():
    workflow= StateGraph(PipelineState)

    workflow.add_node("profiler_node", profiler_node)
    workflow.add_node("anomaly_node",anomaly_node)
    workflow.add_node("root_cause_node",root_cause_node)
    workflow.add_node("impact_node",impact_node)
    workflow.add_node("sql_fix_node",sql_fix_node)
    workflow.add_node("validation_node",validation_node)
    workflow.add_node("contract_node",contract_node)

    workflow.add_edge(START,"profiler_node")
    workflow.add_edge("profiler_node","anomaly_node")
    workflow.add_edge("anomaly_node","root_cause_node")
    workflow.add_edge("root_cause_node","impact_node")
    workflow.add_edge("impact_node","sql_fix_node")
    workflow.add_edge("sql_fix_node","validation_node")
    workflow.add_edge("validation_node","contract_node")
    workflow.add_edge("contract_node", END)

    chain= workflow.compile()

    return chain


