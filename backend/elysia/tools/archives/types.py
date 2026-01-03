"""
Type definitions for the Archives module.

These types define the data structures for:
- Archive sources (Quartermaster output)
- Investigation reports (Case Officer output)
"""

from dataclasses import dataclass, field, asdict
from enum import Enum


class AccessLevel(str, Enum):
    """Access level classification for archive sources."""
    PUBLIC_OPEN = "PUBLIC_OPEN"
    PHYSICAL_ONLY = "PHYSICAL_ONLY"
    RESTRICTED = "RESTRICTED"
    SUBSCRIPTION = "SUBSCRIPTION"
    PHYSICAL_OR_SUBSCRIPTION = "PHYSICAL_OR_SUBSCRIPTION"


class DigitizationStatus(str, Enum):
    """Digitization status of archive content."""
    FULLY_DIGITIZED = "FULLY_DIGITIZED"
    PARTIALLY_DIGITIZED = "PARTIALLY_DIGITIZED"
    NOT_DIGITIZED = "NOT_DIGITIZED"
    N_A = "N_A"


class Protocol(str, Enum):
    """Access protocol for archive sources."""
    WEB_DIGITAL_REPOSITORY = "WEB_DIGITAL_REPOSITORY"
    READING_ROOM_ONLY = "READING_ROOM_ONLY"
    SEARCH_UI_ONLY = "SEARCH_UI_ONLY"
    WIKI_COLLABORATIVE = "WIKI_COLLABORATIVE"
    HTML_CONTENT = "HTML_CONTENT"
    LIBRARY_CATALOGS = "LIBRARY_CATALOGS"
    API = "API"


class ConstraintType(str, Enum):
    """Type of access constraint."""
    LEGAL = "LEGAL"
    TECHNICAL = "TECHNICAL"
    ACCESS_BLOCKED = "ACCESS_BLOCKED"
    LANGUAGE = "LANGUAGE"
    OTHER = "OTHER"


class HypothesisStatus(str, Enum):
    """Status of hypothesis evaluation."""
    CONFIRMED = "CONFIRMED"
    REFUTED = "REFUTED"
    INDETERMINATE = "INDETERMINATE"
    PENDING = "PENDING"


class SourceClassification(str, Enum):
    """Classification of archive source origin.

    INSTITUTIONAL: Pre-configured source from archive_domains.yaml (vetted, high-quality)
    DISCOVERED: Source found during search that is relevant to the investigation
    """
    INSTITUTIONAL = "INSTITUTIONAL"
    DISCOVERED = "DISCOVERED"


@dataclass
class ArchiveConstraint:
    """A constraint affecting access to an archive source."""
    type: ConstraintType
    severity: str  # "low", "medium", "high"
    description: str

    def to_dict(self) -> dict:
        return {
            "type": self.type.value if isinstance(self.type, ConstraintType) else self.type,
            "severity": self.severity,
            "description": self.description,
        }


@dataclass
class ArchiveSource:
    """
    An archive source mapped by the Quartermaster.

    Represents a single archive, database, or academic project that may contain
    relevant information for an investigative query.

    Classification:
    - INSTITUTIONAL: From archive_domains.yaml (vetted, high-quality)
    - DISCOVERED: Found during search, LLM determined as relevant
    """
    id: str
    name: str
    domain: str
    group: str
    summary: str
    access_level: AccessLevel
    digitization_status: DigitizationStatus
    protocol: Protocol
    constraints: list[ArchiveConstraint] = field(default_factory=list)
    notes: str = ""
    source_urls: list[str] = field(default_factory=list)  # Actual URLs with information
    # Classification and relevance fields
    classification: SourceClassification = SourceClassification.INSTITUTIONAL
    relevance_score: float = 0.0  # 0.0-1.0, LLM-assigned for discovered sources
    relevance_reasoning: str = ""  # Why this source is relevant

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "domain": self.domain,
            "group": self.group,
            "summary": self.summary,
            "access_level": self.access_level.value if isinstance(self.access_level, AccessLevel) else self.access_level,
            "digitization_status": self.digitization_status.value if isinstance(self.digitization_status, DigitizationStatus) else self.digitization_status,
            "protocol": self.protocol.value if isinstance(self.protocol, Protocol) else self.protocol,
            "constraints": [c.to_dict() if isinstance(c, ArchiveConstraint) else c for c in self.constraints],
            "notes": self.notes,
            "source_urls": self.source_urls,
            "classification": self.classification.value if isinstance(self.classification, SourceClassification) else self.classification,
            "relevance_score": self.relevance_score,
            "relevance_reasoning": self.relevance_reasoning,
        }


@dataclass
class QuartermasterResult:
    """Result from the Quartermaster tool."""
    archive_sources: list[ArchiveSource]
    query_text: str
    target_collections: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "archive_sources": [s.to_dict() for s in self.archive_sources],
            "query_text": self.query_text,
            "target_collections": self.target_collections,
        }


@dataclass
class Evidence:
    """A piece of evidence supporting or refuting a hypothesis."""
    source_id: str
    content: str
    relevance_score: float = 0.0
    is_positive: bool = True  # True = supports, False = refutes

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Hypothesis:
    """
    An investigative hypothesis generated by the Case Officer.

    Hypotheses are dynamic interpretations of evidence and gaps identified
    during the investigation. They are domain-agnostic and generated based
    on the specific context of each investigation query.
    """
    id: str
    description: str
    status: HypothesisStatus
    confidence: float  # 0.0 to 1.0
    evidence: list[Evidence] = field(default_factory=list)
    reasoning: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "description": self.description,
            "status": self.status.value if isinstance(self.status, HypothesisStatus) else self.status,
            "confidence": self.confidence,
            "evidence": [e.to_dict() for e in self.evidence],
            "reasoning": self.reasoning,
        }


@dataclass
class ReportParagraph:
    """A paragraph in the investigation report with citations."""
    text: str
    ref_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "ref_ids": self.ref_ids,
        }


@dataclass
class InvestigationReport:
    """
    Investigation report synthesized by the Case Officer.

    Contains structured analysis including:
    - Summary findings from all sources (Quartermaster + CaseOfficer discoveries)
    - Hypotheses based on evidence and identified gaps
    - Citations to both Quartermaster and independently discovered sources
    - Actionable next steps with access instructions for protected sources
    """
    title: str
    paragraphs: list[ReportParagraph]
    hypotheses: list[Hypothesis] = field(default_factory=list)
    next_steps: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "paragraphs": [p.to_dict() for p in self.paragraphs],
            "hypotheses": [h.to_dict() for h in self.hypotheses],
            "next_steps": self.next_steps,
        }

    def to_text_objects(self) -> list[dict]:
        """Convert to format expected by Text return object."""
        return [p.to_dict() for p in self.paragraphs]
