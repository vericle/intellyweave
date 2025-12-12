# ABOUTME: Data structures and objects for the intelligence analysis system
# ABOUTME: Defines message types, analysis states, and agent roles for intelligence mode

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from elysia.objects import Result


class IntelligenceRole(Enum):
    """Enumeration of intelligence agent roles"""

    EXTRACTOR = "extractor"
    MAPPER = "mapper"
    SYNTHESIZER = "synthesizer"
    GEOSPATIAL = "geospatial"
    NETWORK = "network"
    PATTERN = "pattern"


class IntelligenceState(Enum):
    """States of the intelligence analysis process"""

    INITIAL_RESPONSE = "initial_response"
    ENTITY_EXTRACTION = "entity_extraction"
    RELATIONSHIP_MAPPING = "relationship_mapping"
    SYNTHESIS = "synthesis"
    GEOSPATIAL_ANALYSIS = "geospatial_analysis"
    NETWORK_ANALYSIS = "network_analysis"
    PATTERN_DETECTION = "pattern_detection"


@dataclass
class IntelligenceMessage(Result):
    """Represents a message from an intelligence agent during analysis"""

    agent_role: IntelligenceRole
    content: str
    findings: List[Dict[str, Any]]
    reasoning: str
    analysis_phase: str
    confidence_score: Optional[float] = None
    suggestions: Optional[List[Dict[str, Any]]] = None

    # Required Result attributes
    objects: List[Dict[str, Any]] = field(init=False)
    metadata: Dict[str, Any] = field(default_factory=dict)
    name: str = field(default="intelligence_message")
    payload_type: str = field(default="intelligence_message")
    mapping: Optional[Dict[str, str]] = field(default=None)
    llm_message: Optional[str] = field(default=None)
    unmapped_keys: List[str] = field(default_factory=lambda: ["_REF_ID"])
    display: bool = field(default=True)

    # Required Return attributes (from parent of Result)
    frontend_type: str = field(default="result", init=False)

    def __post_init__(self):
        """Initialize objects field and Return attributes after dataclass initialization"""
        # Initialize Return attributes (normally done by Return.__init__)
        self.frontend_type = "result"

        # Initialize objects
        self.objects = [
            {
                "content": self.content,
                "findings": self.findings,
            }
        ]
        # Update metadata with intelligence-specific information
        self.metadata.update(
            {
                "agent_role": self.agent_role.value,
                "analysis_phase": self.analysis_phase,
                "confidence_score": self.confidence_score,
                "reasoning": self.reasoning,
            }
        )

    async def to_frontend(
        self,
        user_id: str,
        conversation_id: str,
        query_id: str,
    ):
        """



        Override to_frontend to send intelligence-specific message type.
        Frontend expects message.type to be 'intelligence_extractor', 'intelligence_mapper', 'intelligence_synthesizer', 'intelligence_geospatial', 'intelligence_network' or 'intelligence_pattern'
        """
        if not self.display:
            return

        import uuid

        # Create payload with intelligence agent structure expected by frontend
        payload = {
            "agent_role": self.agent_role.value,
            "content": self.content,
            "findings": self.findings,
            "reasoning": self.reasoning,
            "analysis_phase": self.analysis_phase,
            "confidence_score": self.confidence_score,
            "suggestions": self.suggestions,
        }

        # Set the message type to match frontend expectations
        message_type = f"intelligence_{self.agent_role.value}"

        return {
            "type": message_type,
            "user_id": user_id,
            "conversation_id": conversation_id,
            "query_id": query_id,
            "id": message_type[:3] + "-" + str(uuid.uuid4()),
            "payload": payload,
        }

    def llm_parse(self) -> str:
        """Parse for LLM context"""
        confidence_text = (
            f" (Confidence: {self.confidence_score})" if self.confidence_score else ""
        )
        return (
            f"{self.agent_role.value.capitalize()} Agent ({self.analysis_phase}){confidence_text}: "
            f"{self.content}\n"
            f"Reasoning: {self.reasoning}"
        )


@dataclass
class IntelligenceContext:
    """Context for the ongoing intelligence analysis"""

    initial_query: str
    initial_response: str
    initial_sources: List[Dict[str, Any]]
    analysis_history: List[IntelligenceMessage]
    current_phase: str
    extracted_entities: List[Dict[str, Any]] = field(default_factory=list)
    relationship_map: Dict[str, Any] = field(default_factory=dict)
    visualizations: List[Dict[str, Any]] = field(default_factory=list)

    def add_message(self, message: IntelligenceMessage) -> None:
        """Add a message to the analysis history"""
        self.analysis_history.append(message)

    def get_final_response(self) -> str:
        """Get the final synthesized response"""
        synthesizer_messages = [
            msg
            for msg in self.analysis_history
            if msg.agent_role == IntelligenceRole.SYNTHESIZER
        ]
        if synthesizer_messages:
            return synthesizer_messages[-1].content
        return self.initial_response


@dataclass
class IntelligenceResult(Result):
    """Final result from the intelligence analysis"""

    final_response: str
    analysis_context: IntelligenceContext
    total_phases: int

    # Required Result attributes
    objects: List[Dict[str, Any]] = field(init=False)
    metadata: Dict[str, Any] = field(default_factory=dict)
    name: str = field(default="intelligence_analysis")
    payload_type: str = field(default="intelligence_final")
    mapping: Optional[Dict[str, str]] = field(default=None)
    llm_message: Optional[str] = field(default=None)
    unmapped_keys: List[str] = field(default_factory=lambda: ["_REF_ID"])
    display: bool = field(default=True)

    # Required Return attributes (from parent of Result)
    frontend_type: str = field(default="result", init=False)

    def __post_init__(self):
        """Initialize objects field and Return attributes after dataclass initialization"""
        # Initialize Return attributes (normally done by Return.__init__)
        self.frontend_type = "result"

        # Initialize objects
        self.objects = [
            {
                "text": self.final_response,
            }
        ]
        # Update metadata with intelligence-specific information
        self.metadata.update(
            {
                "total_phases": self.total_phases,
                "analysis_messages": len(self.analysis_context.analysis_history),
            }
        )

    def llm_parse(self) -> str:
        """Parse for LLM context"""
        return (
            f"Intelligence Analysis Result (after {self.total_phases} phases): "
            f"{self.final_response}"
        )


@dataclass
class IntelligenceSuggestionsMessage(Result):
    """Message containing follow-up suggestions for intelligence analysis"""

    suggestions: List[Dict[str, Any]]
    reasoning: str
    analysis_context: IntelligenceContext

    # Required Result attributes
    objects: List[Dict[str, Any]] = field(init=False)
    metadata: Dict[str, Any] = field(default_factory=dict)
    name: str = field(default="intelligence_suggestions")
    payload_type: str = field(default="intelligence_suggestions")
    mapping: Optional[Dict[str, str]] = field(default=None)
    llm_message: Optional[str] = field(default=None)
    unmapped_keys: List[str] = field(default_factory=lambda: ["_REF_ID"])
    display: bool = field(default=True)

    # Required Return attributes (from parent of Result)
    frontend_type: str = field(default="result", init=False)

    def __post_init__(self):
        """Initialize objects field and Return attributes after dataclass initialization"""
        # Initialize Return attributes (normally done by Return.__init__)
        self.frontend_type = "result"

        # Initialize objects
        self.objects = [
            {
                "suggestions": self.suggestions,
            }
        ]
        # Update metadata with suggestions-specific information
        self.metadata.update(
            {
                "suggestion_count": len(self.suggestions),
                "reasoning": self.reasoning,
            }
        )

    async def to_frontend(
        self,
        user_id: str,
        conversation_id: str,
        query_id: str,
    ):
        """
        Override to_frontend to send intelligence suggestions message type.
        """
        if not self.display:
            return

        import uuid

        # Create payload with suggestions structure expected by frontend
        payload = {
            "suggestions": self.suggestions,
            "reasoning": self.reasoning,
        }

        message_type = "intelligence_suggestions"

        return {
            "type": message_type,
            "user_id": user_id,
            "conversation_id": conversation_id,
            "query_id": query_id,
            "id": message_type[:3] + "-" + str(uuid.uuid4()),
            "payload": payload,
        }

    def llm_parse(self) -> str:
        """Parse for LLM context"""
        return f"Intelligence Suggestions: {len(self.suggestions)} follow-up options generated"
