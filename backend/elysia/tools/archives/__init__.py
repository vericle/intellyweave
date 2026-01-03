"""
Archives module for IntellyWeave.

Provides tools for archive discovery and investigative reasoning:
- QuartermasterTool: Maps the information landscape (archives, databases, academic projects)
- CaseOfficerTool: Synthesizes investigation reports with hypothesis validation
"""

from elysia.tools.archives.types import (
    AccessLevel,
    DigitizationStatus,
    Protocol,
    ConstraintType,
    ArchiveConstraint,
    ArchiveSource,
    QuartermasterResult,
    Hypothesis,
    HypothesisStatus,
    Evidence,
    InvestigationReport,
)

__all__ = [
    "AccessLevel",
    "DigitizationStatus",
    "Protocol",
    "ConstraintType",
    "ArchiveConstraint",
    "ArchiveSource",
    "QuartermasterResult",
    "Hypothesis",
    "HypothesisStatus",
    "Evidence",
    "InvestigationReport",
]
