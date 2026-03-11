# backend/core/base_agent.py

class BaseAgent:

    def __init__(self, event_bus, incident_manager):
        self.event_bus = event_bus
        self.incident_manager = incident_manager

    def register(self):
        """
        Subscribe to relevant events.
        """
        raise NotImplementedError

    def handle_event(self, payload: dict):
        """
        Process event payload.
        """
        raise NotImplementedError