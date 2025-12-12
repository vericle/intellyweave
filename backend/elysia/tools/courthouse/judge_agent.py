# ABOUTME: Judge agent implementation for courthouse debate system
# ABOUTME: Acts as neutral moderator ensuring logical and fact-based debate

import dspy
from typing import List, Dict, Any, Optional
from .objects import AgentRole, CourthouseMessage, DebateContext


class JudgeEvaluation(dspy.Signature):
    """Evaluate arguments and maintain neutrality in the debate"""
    query = dspy.InputField(desc="The original user query")
    initial_response = dspy.InputField(desc="The initial response being debated")
    defense_argument = dspy.InputField(desc="Defense agent's argument")
    prosecution_argument = dspy.InputField(desc="Prosecution agent's counter-argument")
    debate_history = dspy.InputField(desc="History of the debate so far")

    evaluation = dspy.OutputField(desc="Neutral evaluation of both arguments")
    consensus_possible = dspy.OutputField(desc="Whether consensus can be reached (true/false)")
    reasoning = dspy.OutputField(desc="Logical reasoning for the evaluation")
    final_verdict = dspy.OutputField(desc="If consensus reached, the final agreed-upon answer")


class JudgeAgent:
    """Judge agent that moderates the courthouse debate"""

    def __init__(self, base_lm: dspy.LM):
        """Initialize the judge agent

        Args:
            base_lm: The language model to use for evaluation
        """
        self.lm = base_lm
        self.evaluator = dspy.ChainOfThought(JudgeEvaluation)

    async def evaluate(
        self,
        context: DebateContext,
        defense_argument: Optional[CourthouseMessage] = None,
        prosecution_argument: Optional[CourthouseMessage] = None,
    ) -> CourthouseMessage:
        """Evaluate the current state of the debate

        Args:
            context: The debate context
            defense_argument: Latest defense argument if any
            prosecution_argument: Latest prosecution argument if any

        Returns:
            CourthouseMessage with judge's evaluation
        """
        # Prepare debate history summary
        debate_summary = self._summarize_debate(context.debate_history)

        # Get arguments text
        defense_text = defense_argument.argument if defense_argument else "No defense argument yet"
        prosecution_text = prosecution_argument.argument if prosecution_argument else "No prosecution argument yet"

        with dspy.context(lm=self.lm):
            result = self.evaluator(
                query=context.initial_query,
                initial_response=context.initial_response,
                defense_argument=defense_text,
                prosecution_argument=prosecution_text,
                debate_history=debate_summary
            )

        # Determine if consensus is reached
        consensus_reached = result.consensus_possible.lower() == "true"

        # Create judge message
        evaluation_text = result.evaluation
        if consensus_reached:
            evaluation_text = f"CONSENSUS REACHED: {result.final_verdict}"

        return CourthouseMessage(
            agent_role=AgentRole.JUDGE,
            argument=evaluation_text,
            supporting_sources=[],  # Judge doesn't provide sources, only evaluation
            reasoning=result.reasoning,
            debate_round=context.current_round,
            agrees_with_consensus=consensus_reached
        )

    def _summarize_debate(self, history: List[CourthouseMessage]) -> str:
        """Summarize the debate history for context

        Args:
            history: List of courthouse messages

        Returns:
            Summary string of the debate
        """
        if not history:
            return "Debate just started"

        summary_parts = []
        for msg in history:
            role = msg.agent_role.value.capitalize()
            summary_parts.append(f"Round {msg.debate_round} - {role}: {msg.argument[:200]}...")

        return "\n".join(summary_parts)

    async def initial_assessment(
        self,
        query: str,
        initial_response: str,
        sources: List[Dict[str, Any]]
    ) -> str:
        """Provide initial assessment before debate begins

        Args:
            query: Original user query
            initial_response: Initial response to evaluate
            sources: Supporting sources

        Returns:
            Initial judge assessment
        """
        assessment_prompt = f"""
        As a neutral judge, assess this initial response to determine if it requires debate:

        Query: {query}
        Initial Response: {initial_response}
        Number of sources: {len(sources)}

        Provide a brief assessment of the response quality and whether courthouse debate would improve it.
        """

        with dspy.context(lm=self.lm):
            response = self.lm(assessment_prompt)

        return response