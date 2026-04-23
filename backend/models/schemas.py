from __future__ import annotations

from typing import List, Optional, Literal

from pydantic import BaseModel, Field


Level = Literal["heavy", "medium", "safe"]


class SentenceItem(BaseModel):
    id: int
    paragraph_index: int
    original: str
    rewritten: str
    similarity: float = 0.0
    level: Level = "safe"
    locked: bool = False


class DocumentStats(BaseModel):
    total: int
    heavy: int
    medium: int
    safe: int
    heavy_ratio: float
    score: int


class VersionSnapshot(BaseModel):
    version: int
    title: str
    items: List[SentenceItem]


class DocumentSession(BaseModel):
    session_id: str
    filename: str
    paragraphs: List[str] = Field(default_factory=list)
    items: List[SentenceItem] = Field(default_factory=list)
    logs: List[str] = Field(default_factory=list)
    versions: List[VersionSnapshot] = Field(default_factory=list)


class ProcessResponse(BaseModel):
    session_id: str
    filename: str
    items: List[SentenceItem]
    stats: DocumentStats
    versions: List[VersionSnapshot]
    logs: List[str]


class RewriteRequest(BaseModel):
    session_id: str


class EditSentenceRequest(BaseModel):
    text: str


class LockAllRequest(BaseModel):
    session_id: str
    locked: bool


class VersionSwitchRequest(BaseModel):
    session_id: str
    version: int


class AutoOptimizeStepResponse(BaseModel):
    done: bool
    message: str
    optimized_sentence_id: Optional[int] = None
    items: List[SentenceItem]
    stats: DocumentStats
    logs: List[str]
