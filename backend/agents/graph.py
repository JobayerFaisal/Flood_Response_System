# backend/agents/graph.py
# This file defines the state graph for the flood response system, connecting all agents in a logical flow.

from langgraph.graph import StateGraph, END
from backend.agents.state import AgentState
from backend.agents.triage_agent import triage_agent
from backend.agents.cluster_agent import cluster_agent
from backend.agents.resource_agent import resource_agent
from backend.agents.routing_agent import routing_agent
from backend.agents.medical_agent import medical_agent
from backend.agents.command_agent import command_agent


def build_graph():

    builder = StateGraph(AgentState)

    builder.add_node("triage", triage_agent)
    builder.add_node("cluster", cluster_agent)
    builder.add_node("resource", resource_agent)
    builder.add_node("routing", routing_agent)
    builder.add_node("medical", medical_agent)
    builder.add_node("command", command_agent)

    builder.set_entry_point("triage")

    builder.add_edge("triage", "cluster")
    builder.add_edge("cluster", "resource")
    builder.add_edge("resource", "routing")
    builder.add_edge("routing", "medical")
    builder.add_edge("medical", "command")

    # 🔥 THIS WAS MISSING
    builder.add_edge("command", END)

    return builder.compile()