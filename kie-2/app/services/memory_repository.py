from abc import ABC, abstractmethod
import threading
from typing import Dict, List, Optional
from app.schemas.memory import LearnerMemory
from app.schemas.memory_events import MemoryUpdateEvent


class BaseMemoryRepository(ABC):
    """Abstract persistence interface for learner memory intelligence.
    Ensures AI/ML-2 logic is strictly decoupled from the underlying database implementation.
    """

    @abstractmethod
    def get_memory(self, learner_id: str) -> Optional[LearnerMemory]:
        """Retrieve the current memory intelligence container for a learner."""
        pass

    @abstractmethod
    def save_memory(self, memory: LearnerMemory) -> LearnerMemory:
        """Persist or update a learner's memory container."""
        pass

    @abstractmethod
    def record_event(self, event: MemoryUpdateEvent) -> None:
        """Record an append-only raw learning evidence event."""
        pass

    @abstractmethod
    def list_events(self, learner_id: str, limit: int = 50) -> List[MemoryUpdateEvent]:
        """Retrieve recent chronological activity events for a learner."""
        pass

    @abstractmethod
    def clear(self, learner_id: Optional[str] = None) -> None:
        """Reset memory store for testing and isolation."""
        pass


class InMemoryMemoryRepository(BaseMemoryRepository):
    """Thread-safe, in-memory repository implementation for AI/ML-2 runtime and test isolation.
    Enables zero external database dependency while honoring the Backend persistence boundary.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._memories: Dict[str, LearnerMemory] = {}
        self._events: Dict[str, List[MemoryUpdateEvent]] = {}

    def get_memory(self, learner_id: str) -> Optional[LearnerMemory]:
        with self._lock:
            memory = self._memories.get(learner_id)
            if memory:
                # Return deep copy via model_validate to prevent accidental out-of-band mutation
                return LearnerMemory.model_validate(memory.model_dump())
            return None

    def save_memory(self, memory: LearnerMemory) -> LearnerMemory:
        with self._lock:
            self._memories[memory.learner_id] = LearnerMemory.model_validate(memory.model_dump())
            return self._memories[memory.learner_id]

    def record_event(self, event: MemoryUpdateEvent) -> None:
        with self._lock:
            if event.learner_id not in self._events:
                self._events[event.learner_id] = []
            self._events[event.learner_id].append(event)

    def list_events(self, learner_id: str, limit: int = 50) -> List[MemoryUpdateEvent]:
        with self._lock:
            events = self._events.get(learner_id, [])
            return list(reversed(events[-limit:]))

    def clear(self, learner_id: Optional[str] = None) -> None:
        with self._lock:
            if learner_id:
                self._memories.pop(learner_id, None)
                self._events.pop(learner_id, None)
            else:
                self._memories.clear()
                self._events.clear()
