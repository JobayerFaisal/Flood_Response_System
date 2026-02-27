# Agent State Model
# backend/agents/state.py

from typing import Dict, Any, List
from pydantic import BaseModel


class AgentState(BaseModel):
    flood_event: Dict[str, Any]
    reports: List[Dict[str, Any]]

    triaged_reports: List[Dict[str, Any]] = []
    clusters: Dict[int, int] = {}
    allocation_plan: Dict[int, Any] = {}
    routes: Dict[int, Any] = {}
    medical_flags: List[Dict[str, Any]] = []
    final_plan: Dict[str, Any] = {}