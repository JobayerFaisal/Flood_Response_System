# backend/core/event_bus.py

from collections import defaultdict
from typing import Callable, Dict, List


class EventBus:

    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._event_log: List[dict] = []

    def subscribe(self, event_type: str, handler: Callable):
        self._subscribers[event_type].append(handler)

    def publish(self, event_type: str, payload: dict):

        event_record = {
            "event_type": event_type,
            "payload": payload
        }

        self._event_log.append(event_record)

        if event_type in self._subscribers:
            for handler in self._subscribers[event_type]:
                handler(payload)

    def get_event_log(self):
        return self._event_log