# ABOUTME: Data structures and objects for the courthouse debate system
# ABOUTME: Defines message types, debate states, and agent roles for courthouse mode

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any
from elysia.objects import Result


class AgentRole(Enum):
    """Enumeration of courthouse agent roles"""
    JUDGE = "judge"
    DEFENSE = "defense"
    PROSECUTION = "prosecution"


class DebateState(Enum):
    """States of the courthouse debate process"""
    INITIAL_RESPONSE = "initial_response"
    DEFENSE_ARGUMENT = "defense_argument"
    PROSECUTION_ARGUMENT = "prosecution_argument"
    JUDGE_EVALUATION = "judge_evaluation"
    CONSENSUS_REACHED = "consensus_reached"
    CONSENSUS_FAILED = "consensus_failed"


@dataclass
class CourthouseMessage(Result):
    """Represents a message from a courthouse agent during debate"""
    agent_role: AgentRole
    argument: str
    supporting_sources: List[Dict[str, Any]]
    reasoning: str
    debate_round: int
    agrees_with_consensus: Optional[bool] = None

    # Required Result attributes
    objects: List[Dict[str, Any]] = field(init=False)
    metadata: Dict[str, Any] = field(default_factory=dict)
    name: str = field(default="courthouse_message")
    payload_type: str = field(default="courthouse_message")
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
        self.objects = [{
            "argument": self.argument,
            "supporting_sources": self.supporting_sources,
        }]
        # Update metadata with courthouse-specific information
        self.metadata.update({
            "agent_role": self.agent_role.value,
            "debate_round": self.debate_round,
            "agrees_with_consensus": self.agrees_with_consensus,
            "reasoning": self.reasoning,
        })

    async def to_frontend(
        self,
        user_id: str,
        conversation_id: str,
        query_id: str,
    ):
        """
        Override to_frontend to send courthouse-specific message type.
        Frontend expects message.type to be 'courthouse_judge', 'courthouse_defense', or 'courthouse_prosecution'
        """
        if not self.display:
            return

        import uuid

        # Create payload with courthouse agent structure expected by frontend
        payload = {
            "agent_role": self.agent_role.value,
            "argument": self.argument,
            "supporting_sources": self.supporting_sources,
            "reasoning": self.reasoning,
            "debate_round": self.debate_round,
            "agrees_with_consensus": self.agrees_with_consensus,
        }

        # Set the message type to match frontend expectations
        message_type = f"courthouse_{self.agent_role.value}"

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
        consensus_text = ""
        if self.agrees_with_consensus is not None:
            consensus_text = f" (Agrees with consensus: {self.agrees_with_consensus})"

        return (
            f"{self.agent_role.value.capitalize()} Agent (Round {self.debate_round}){consensus_text}: "
            f"{self.argument}\n"
            f"Reasoning: {self.reasoning}"
        )


@dataclass
class DebateContext:
    """Context for the ongoing courthouse debate"""
    initial_query: str
    initial_response: str
    initial_sources: List[Dict[str, Any]]
    debate_history: List[CourthouseMessage]
    current_round: int
    max_rounds: int = 5  # Maximum debate rounds to prevent infinite loops
    prosecution_counter_arguments: int = 0
    max_prosecution_arguments: int = 3  # Maximum 2-3 counter arguments as specified

    def add_message(self, message: CourthouseMessage) -> None:
        """Add a message to the debate history"""
        self.debate_history.append(message)
        if message.agent_role == AgentRole.PROSECUTION:
            self.prosecution_counter_arguments += 1

    def can_prosecution_argue(self) -> bool:
        """Check if prosecution can still make arguments"""
        return self.prosecution_counter_arguments < self.max_prosecution_arguments

    def has_consensus(self) -> bool:
        """Check if all agents have reached consensus"""
        # Need at least one message from each agent
        roles_present = set(msg.agent_role for msg in self.debate_history)
        if len(roles_present) < 3:
            return False

        # Check last round - all agents should agree
        last_round_messages = [
            msg for msg in self.debate_history
            if msg.debate_round == self.current_round
        ]

        if len(last_round_messages) < 3:
            return False

        return all(
            msg.agrees_with_consensus == True
            for msg in last_round_messages
        )

    def get_final_response(self) -> str:
        """Get the final consensus response"""
        if not self.has_consensus():
            return self.initial_response  # Fallback to initial if no consensus

        # Find the last judge's evaluation as the final response
        judge_messages = [
            msg for msg in self.debate_history
            if msg.agent_role == AgentRole.JUDGE
        ]

        if judge_messages:
            return judge_messages[-1].argument

        return self.initial_response


@dataclass
class CourthouseResult(Result):
    """Final result from the courthouse debate"""
    final_response: str
    debate_context: DebateContext
    consensus_reached: bool
    total_rounds: int

    # Required Result attributes
    objects: List[Dict[str, Any]] = field(init=False)
    metadata: Dict[str, Any] = field(default_factory=dict)
    name: str = field(default="courthouse_consensus")
    payload_type: str = field(default="courthouse_final")
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
        self.objects = [{
            "text": self.final_response,
            "consensus": self.consensus_reached,
        }]
        # Update metadata with courthouse-specific information
        self.metadata.update({
            "consensus_reached": self.consensus_reached,
            "total_rounds": self.total_rounds,
            "debate_messages": len(self.debate_context.debate_history),
        })

    def llm_parse(self) -> str:
        """Parse for LLM context"""
        consensus_status = "reached" if self.consensus_reached else "not reached"
        return (
            f"Courthouse Debate Result (Consensus {consensus_status} after {self.total_rounds} rounds): "
            f"{self.final_response}"
        )