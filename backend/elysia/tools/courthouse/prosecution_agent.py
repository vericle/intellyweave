# ABOUTME: Prosecution agent implementation for courthouse debate system
# ABOUTME: Provides logical counter-arguments to improve response quality

import dspy
from typing import List, Dict, Any, Optional
from .objects import AgentRole, CourthouseMessage, DebateContext


class ProsecutionChallenge(dspy.Signature):
    """Construct logical challenges to the response"""
    query = dspy.InputField(desc="The original user query")
    initial_response = dspy.InputField(desc="The response to challenge")
    defense_argument = dspy.InputField(desc="Defense's latest argument")
    debate_history = dspy.InputField(desc="History of the debate")
    previous_challenges = dspy.InputField(desc="Previous challenges made")

    challenge = dspy.OutputField(desc="Logical challenge to the response or defense")
    specific_issues = dspy.OutputField(desc="Specific logical flaws or missing elements")
    reasoning = dspy.OutputField(desc="Reasoning behind the challenge")
    constructive_suggestion = dspy.OutputField(desc="How the response could be improved")
    convince_threshold_reached = dspy.OutputField(desc="Whether prosecution is convinced (true/false)")


class ProsecutionAgent:
    """Prosecution agent that critically evaluates responses"""

    def __init__(self, base_lm: dspy.LM):
        """Initialize the prosecution agent

        Args:
            base_lm: The language model to use for challenges
        """
        self.lm = base_lm
        self.challenger = dspy.ChainOfThought(ProsecutionChallenge)
        # Agent should be easily convincible - max 2-3 counter arguments
        self.conviction_threshold = 0.7  # High threshold for being convinced

    async def challenge(
        self,
        context: DebateContext,
        defense_argument: CourthouseMessage
    ) -> Optional[CourthouseMessage]:
        """Construct prosecution challenge

        Args:
            context: The debate context
            defense_argument: Latest defense argument

        Returns:
            CourthouseMessage with challenge or None if convinced
        """
        # Check if prosecution has reached argument limit
        if not context.can_prosecution_argue():
            return None

        # Prepare previous challenges summary
        previous_challenges = self._get_previous_challenges(context.debate_history)

        # Prepare debate history
        debate_summary = self._summarize_debate(context.debate_history)

        with dspy.context(lm=self.lm):
            result = self.challenger(
                query=context.initial_query,
                initial_response=context.initial_response,
                defense_argument=defense_argument.argument,
                debate_history=debate_summary,
                previous_challenges=previous_challenges
            )

        # Check if prosecution is convinced
        is_convinced = result.convince_threshold_reached.lower() == "true"

        if is_convinced:
            # Prosecution agrees with consensus
            return CourthouseMessage(
                agent_role=AgentRole.PROSECUTION,
                argument=f"After careful consideration, the defense has addressed my concerns. {result.constructive_suggestion}",
                supporting_sources=[],
                reasoning="The defense arguments are logically sound and comprehensive",
                debate_round=context.current_round,
                agrees_with_consensus=True
            )

        # Construct challenge message
        challenge_text = result.challenge
        if result.specific_issues:
            challenge_text += f"\n\nSpecific concerns: {result.specific_issues}"
        if result.constructive_suggestion:
            challenge_text += f"\n\nSuggestion: {result.constructive_suggestion}"

        return CourthouseMessage(
            agent_role=AgentRole.PROSECUTION,
            argument=challenge_text,
            supporting_sources=[],  # Prosecution uses logic, not sources
            reasoning=result.reasoning,
            debate_round=context.current_round,
            agrees_with_consensus=False
        )

    def _get_previous_challenges(self, history: List[CourthouseMessage]) -> str:
        """Get summary of previous prosecution challenges

        Args:
            history: Debate history

        Returns:
            Summary of previous challenges
        """
        prosecution_messages = [
            msg for msg in history
            if msg.agent_role == AgentRole.PROSECUTION
        ]

        if not prosecution_messages:
            return "No previous challenges"

        challenges = []
        for msg in prosecution_messages:
            challenges.append(f"Round {msg.debate_round}: {msg.argument[:100]}...")

        return "\n".join(challenges)

    def _summarize_debate(self, history: List[CourthouseMessage]) -> str:
        """Summarize the debate history for context

        Args:
            history: List of courthouse messages

        Returns:
            Summary string of the debate
        """
        if not history:
            return "Beginning of debate"

        summary_parts = []
        for msg in history[-3:]:  # Last 3 messages for context
            role = msg.agent_role.value.capitalize()
            consensus = "(agrees)" if msg.agrees_with_consensus else ""
            summary_parts.append(f"{role} {consensus}: {msg.argument[:150]}...")

        return "\n".join(summary_parts)

    async def evaluate_initial_response(
        self,
        query: str,
        response: str,
        sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Evaluate the initial response for potential issues

        Args:
            query: User query
            response: Initial response
            sources: Supporting sources

        Returns:
            Evaluation dictionary
        """
        evaluation_prompt = f"""
        As a critical evaluator, identify potential issues with this response:

        Query: {query}
        Response: {response}
        Sources available: {len(sources)}

        Identify:
        1. Logical gaps or inconsistencies
        2. Missing information
        3. Potential biases
        4. Areas needing clarification

        Be constructive and objective. Maximum 2-3 main issues.
        """

        with dspy.context(lm=self.lm):
            evaluation = self.lm(evaluation_prompt)

        return {
            "has_issues": bool(evaluation),
            "evaluation": evaluation
        }