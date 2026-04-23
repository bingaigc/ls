from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from backend.models.schemas import DocumentSession


@dataclass
class SessionStore:
    sessions: Dict[str, DocumentSession] = field(default_factory=dict)

    def get(self, session_id: str) -> DocumentSession:
        if session_id not in self.sessions:
            raise KeyError(f"Session not found: {session_id}")
        return self.sessions[session_id]

    def set(self, session: DocumentSession) -> None:
        self.sessions[session.session_id] = session


store = SessionStore()
