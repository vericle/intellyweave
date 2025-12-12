# ABOUTME: Defense agent implementation for courthouse debate system
# ABOUTME: Defends the initial response using provided sources and logical arguments

import dspy
from typing import List, Dict, Any
from .objects import AgentRole, CourthouseMessage, DebateContext


class DefenseArgument(dspy.Signature):
    """Construct a defense for the initial response"""
    query = dspy.InputField(desc="The original user query")
    initial_response = dspy.InputField(desc="The response to defend")
    available_sources = dspy.InputField(desc="Sources supporting the response")
    prosecution_challenge = dspy.InputField(desc="Challenge from prosecution if any")
    debate_history = dspy.InputField(desc="History of the debate")

    defense = dspy.OutputField(desc="Strong defense of the initial response")
    key_evidence = dspy.OutputField(desc="Key evidence from sources supporting the response")
    reasoning = dspy.OutputField(desc="Logical reasoning for the defense")
    addresses_challenges = dspy.OutputField(desc="How this addresses prosecution's challenges")


class DefenseAgent:
    """Defense agent that supports the initial response with evidence"""

    def __init__(self, base_lm: dspy.LM):
        """Initialize the defense agent

        Args:
            base_lm: The language model to use for arguments
        """
        self.lm = base_lm
        self.argument_builder = dspy.ChainOfThought(DefenseArgument)

    async def defend(
        self,
        context: DebateContext,
        prosecution_challenge: CourthouseMessage = None
    ) -> CourthouseMessage:
        """Construct defense argument

        Args:
            context: The debate context
            prosecution_challenge: Latest prosecution challenge if any

        Returns:
            CourthouseMessage with defense argument
        """
        # Prepare sources summary
        sources_summary = self._summarize_sources(context.initial_sources)

        # Get prosecution challenge text
        challenge_text = (
            prosecution_challenge.argument if prosecution_challenge
            else "No challenges yet - presenting initial defense"
        )

        # Prepare debate history
        debate_summary = self._summarize_debate(context.debate_history)

        with dspy.context(lm=self.lm):
            result = self.argument_builder(
                query=context.initial_query,
                initial_response=context.initial_response,
                available_sources=sources_summary,
                prosecution_challenge=challenge_text,
                debate_history=debate_summary
            )

        # Extract key evidence as supporting sources
        supporting_sources = self._extract_evidence_sources(
            result.key_evidence,
            context.initial_sources
        )

        # Construct defense message
        defense_text = result.defense
        if result.addresses_challenges and prosecution_challenge:
            defense_text += f"\n\nAddressing challenges: {result.addresses_challenges}"

        return CourthouseMessage(
            agent_role=AgentRole.DEFENSE,
            argument=defense_text,
            supporting_sources=supporting_sources,
            reasoning=result.reasoning,
            debate_round=context.current_round,
            agrees_with_consensus=None  # Set by debate orchestrator
        )

    def _summarize_sources(self, sources: List[Dict[str, Any]]) -> str:
        """Summarize available sources for the defense

        Args:
            sources: List of source documents

        Returns:
            Summary string of sources
        """
        if not sources:
            return "No specific sources available"

        summary_parts = []
        for i, source in enumerate(sources[:5], 1):  # Limit to first 5 sources
            # Extract relevant fields based on source structure
            title = source.get("title", source.get("name", f"Source {i}"))
            content = source.get("content", source.get("text", ""))[:200]
            summary_parts.append(f"{i}. {title}: {content}...")

        return "\n".join(summary_parts)

    def _summarize_debate(self, history: List[CourthouseMessage]) -> str:
        """Summarize the debate history for context

        Args:
            history: List of courthouse messages

        Returns:
            Summary string of the debate
        """
        if not history:
            return "Beginning of debate"

        # Focus on prosecution challenges
        prosecution_messages = [
            msg for msg in history
            if msg.agent_role == AgentRole.PROSECUTION
        ]

        if not prosecution_messages:
            return "No prosecution challenges yet"

        summary_parts = []
        for msg in prosecution_messages:
            summary_parts.append(f"Challenge (Round {msg.debate_round}): {msg.argument[:150]}...")

        return "\n".join(summary_parts)

    def _extract_evidence_sources(
        self,
        evidence_text: str,
        available_sources: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Extract relevant sources mentioned in the evidence

        Args:
            evidence_text: Text describing key evidence
            available_sources: All available sources

        Returns:
            List of relevant sources
        """
        # Simple extraction - return first 3 sources mentioned or available
        # In production, this would do more sophisticated matching
        relevant_sources = []

        for source in available_sources[:3]:
            relevant_sources.append({
                "title": source.get("title", source.get("name", "Source")),
                "excerpt": source.get("content", source.get("text", ""))[:200],
                "relevance": "Supporting evidence"
            })

        return relevant_sources