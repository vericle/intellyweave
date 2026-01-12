# ABOUTME: Main courthouse debate orchestration tool that coordinates all agents
# ABOUTME: Manages turn-based debate flow, consensus detection, and response refinement

from typing import AsyncGenerator, Dict, Any, List
import asyncio

from elysia.objects import Tool, Text, Update, Error, Status, Response
from elysia.tree.objects import TreeData
from elysia.util.client import ClientManager

from .objects import (
    AgentRole,
    DebateState,
    CourthouseMessage,
    DebateContext,
    CourthouseResult,
)
from .judge_agent import JudgeAgent
from .defense_agent import DefenseAgent
from .prosecution_agent import ProsecutionAgent


class CourthouseDebate(Tool):
    """
    Main tool for conducting courthouse-style debate on query responses.
    Coordinates Judge, Defense, and Prosecution agents to refine answers through debate.
    """

    def __init__(self, logger, **kwargs):
        """Initialize the courthouse debate tool

        Args:
            logger: Logger instance for tracking debate progress
            **kwargs: Additional arguments for tool initialization
        """
        self.logger = logger
        super().__init__(
            name="courthouse_debate",
            description=(
                "Conducts a courthouse-style debate with three agents (Judge, Defense, Prosecution) "
                "to critically evaluate and refine the initial response. The debate continues until "
                "consensus is reached or maximum rounds are completed."
            ),
            inputs={
                "initial_query": {
                    "description": "The original user query",
                    "type": "string",
                    "required": True,
                },
                "initial_response": {
                    "description": "The initial response to be debated",
                    "type": "string",
                    "required": True,
                },
                "initial_sources": {
                    "description": "Sources supporting the initial response",
                    "type": "list",
                    "required": False,
                    "default": [],
                },
            },
            end=True,
            status="Conducting courthouse debate...",
            **kwargs,
        )

    async def __call__(
        self,
        tree_data: TreeData,
        inputs: Dict[str, Any],
        base_lm,
        complex_lm,
        client_manager: ClientManager,
        **kwargs,
    ) -> AsyncGenerator[CourthouseMessage | CourthouseResult | Status | Response | Error, None]:
        """
        Execute the courthouse debate workflow

        Args:
            tree_data: Tree data containing conversation context
            inputs: Tool inputs (initial_query, initial_response, initial_sources)
            base_lm: Base language model
            complex_lm: Complex language model
            client_manager: Client manager for database operations
            **kwargs: Additional arguments

        Yields:
            Debate messages, updates, and final result
        """
        self.logger.info("Starting courthouse debate")

        try:
            # Extract inputs
            initial_query = inputs.get("initial_query", "")
            initial_response = inputs.get("initial_response", "")
            initial_sources = inputs.get("initial_sources", [])

            # Validate inputs
            if not initial_query or not initial_response:
                yield Error(
                    error_message="Missing required inputs for courthouse debate",
                    feedback="Please provide both initial_query and initial_response"
                )
                return

            # Initialize debate context
            debate_context = DebateContext(
                initial_query=initial_query,
                initial_response=initial_response,
                initial_sources=initial_sources,
                debate_history=[],
                current_round=1,
                max_rounds=5,
                prosecution_counter_arguments=0,
                max_prosecution_arguments=3,
            )

            # Initialize agents
            judge = JudgeAgent(base_lm=base_lm)
            defense = DefenseAgent(base_lm=base_lm)
            prosecution = ProsecutionAgent(base_lm=base_lm)

            yield Status("Courthouse debate initiated. Judge, Defense, and Prosecution agents are ready.")

            # Conduct debate rounds
            consensus_reached = False

            while (
                debate_context.current_round <= debate_context.max_rounds
                and not consensus_reached
            ):
                self.logger.info(f"Starting debate round {debate_context.current_round}")

                yield Status(f"Debate Round {debate_context.current_round} starting...")

                # Defense presents argument
                yield Status("Defense agent presenting argument...")
                prosecution_last = self._get_last_prosecution(debate_context)
                defense_msg = await defense.defend(
                    context=debate_context,
                    prosecution_challenge=prosecution_last
                )
                debate_context.add_message(defense_msg)
                yield defense_msg

                # Prosecution evaluates and challenges
                yield Status("Prosecution agent evaluating...")
                prosecution_msg = await prosecution.challenge(
                    context=debate_context,
                    defense_argument=defense_msg
                )

                if prosecution_msg is None:
                    # Prosecution has reached maximum arguments
                    yield Status("Prosecution has completed maximum number of challenges.")
                    # Create agreement message
                    prosecution_msg = CourthouseMessage(
                        agent_role=AgentRole.PROSECUTION,
                        argument="No further challenges. The defense has adequately addressed the query.",
                        supporting_sources=[],
                        reasoning="Maximum challenge limit reached",
                        debate_round=debate_context.current_round,
                        agrees_with_consensus=True
                    )

                debate_context.add_message(prosecution_msg)
                yield prosecution_msg

                # Judge evaluates both arguments
                yield Status("Judge evaluating arguments...")
                judge_msg = await judge.evaluate(
                    context=debate_context,
                    defense_argument=defense_msg,
                    prosecution_argument=prosecution_msg
                )
                debate_context.add_message(judge_msg)
                yield judge_msg

                # Check for consensus
                if self._check_consensus(debate_context):
                    consensus_reached = True
                    yield Status("✓ Consensus reached by all agents!")
                    break

                # Check if prosecution is satisfied
                if prosecution_msg.agrees_with_consensus:
                    consensus_reached = True
                    yield Status("✓ Prosecution agrees with defense - consensus reached!")
                    break

                # Move to next round if no consensus
                if debate_context.current_round < debate_context.max_rounds:
                    debate_context.current_round += 1
                    yield Status(f"No consensus yet. Moving to round {debate_context.current_round}...")
                else:
                    yield Status("Maximum debate rounds reached. Concluding with current state.")

            # Generate final result
            final_response = debate_context.get_final_response()

            # Create final result
            result = CourthouseResult(
                final_response=final_response,
                debate_context=debate_context,
                consensus_reached=consensus_reached,
                total_rounds=debate_context.current_round
            )

            yield result

            # Yield final text response
            consensus_text = "after reaching consensus" if consensus_reached else "after thorough debate"
            yield Response(f"{final_response}\n\n[Courthouse Mode: Final response {consensus_text} across {debate_context.current_round} rounds]")

            self.logger.info(
                f"Courthouse debate completed. Consensus: {consensus_reached}, "
                f"Rounds: {debate_context.current_round}"
            )

        except Exception as e:
            self.logger.exception("Error during courthouse debate")
            yield Error(
                error_message=f"Courthouse debate failed: {str(e)}",
                feedback="An error occurred during the debate process. Falling back to initial response."
            )
            # Fallback to initial response on error
            yield Response(inputs.get("initial_response", ""))

    def _get_last_prosecution(
        self, context: DebateContext
    ) -> CourthouseMessage | None:
        """Get the last prosecution message from debate history

        Args:
            context: Debate context

        Returns:
            Last prosecution message or None
        """
        for msg in reversed(context.debate_history):
            if msg.agent_role == AgentRole.PROSECUTION:
                return msg
        return None

    def _check_consensus(self, context: DebateContext) -> bool:
        """Check if consensus has been reached among all agents

        Args:
            context: Debate context

        Returns:
            True if consensus is reached
        """
        # Get messages from current round
        current_round_messages = [
            msg for msg in context.debate_history
            if msg.debate_round == context.current_round
        ]

        # Need all three agents to have responded
        if len(current_round_messages) < 3:
            return False

        # Check if all agents agree
        judge_agrees = any(
            msg.agent_role == AgentRole.JUDGE and msg.agrees_with_consensus == True
            for msg in current_round_messages
        )

        defense_present = any(
            msg.agent_role == AgentRole.DEFENSE
            for msg in current_round_messages
        )

        prosecution_agrees = any(
            msg.agent_role == AgentRole.PROSECUTION and msg.agrees_with_consensus == True
            for msg in current_round_messages
        )

        return judge_agrees and defense_present and prosecution_agrees

    def get_default_inputs(self) -> Dict[str, Any]:
        """Get default input values

        Returns:
            Dictionary of default inputs
        """
        return {
            "initial_query": "",
            "initial_response": "",
            "initial_sources": [],
        }
