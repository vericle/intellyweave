# ABOUTME: Router agent that classifies user queries into specialized domains
# ABOUTME: Evaluates query and routes to appropriate custom user-defined agents

import logging
from logging import Logger
from typing import AsyncGenerator

import dspy

from elysia.objects import Response, Status, Tool
from elysia.tools.domain.objects import DomainClassification
from elysia.tools.domain.prompt_templates import create_domain_router_prompt
from elysia.tree.objects import TreeData
from elysia.util.client import ClientManager
from elysia.util.elysia_chain_of_thought import ElysiaChainOfThought

module_logger = logging.getLogger(__name__)


class DomainRouter(Tool):
    """
    Domain routing agent that classifies user queries.

    Evaluates whether a query requires specialized knowledge from any
    custom user-defined agents. If a match is found, sets classification
    in hidden_environment to route to the appropriate custom agent.
    Otherwise, proceeds with general processing.
    """

    def __init__(
        self,
        logger: Logger | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            name="domain_router",
            description=(
                "Evaluates if the query requires specialized domain knowledge from custom agents. "
                "Routes to appropriate custom specialized agents when their expertise is needed. "
                "Use this first to determine if specialized handling is needed."
            ),
            status="Evaluating query domain...",
            inputs={},
            end=False,
        )
        self.logger = logger or module_logger
        self.logger.debug(
            "DomainRouter initialized (custom_logger=%s)",
            logger is not None,
        )

    async def is_tool_available(
        self,
        tree_data: TreeData,
        base_lm: dspy.LM,
        complex_lm: dspy.LM,
        client_manager: ClientManager | None = None,
        **kwargs,
    ) -> bool:
        """
        Router should only run once per query.

        Returns False if domain classification has already been performed,
        preventing infinite loops where router runs on every iteration.
        """
        classification_exists = (
            "domain_classification" in tree_data.environment.hidden_environment
        )

        if self.logger:
            self.logger.debug(
                "Domain Router availability check: existing_classification=%s",
                classification_exists,
            )

        if self.logger and classification_exists:
            self.logger.debug(
                "Domain Router not available - classification already performed: "
                f"{tree_data.environment.hidden_environment['domain_classification']['domain']}"
            )

        # Return True only if no classification has been made yet
        return not classification_exists

    async def __call__(
        self,
        tree_data: TreeData,
        inputs: dict,
        base_lm: dspy.LM,
        complex_lm: dspy.LM,
        client_manager: ClientManager | None = None,
        **kwargs,
    ) -> AsyncGenerator:
        """
        Classify the user query into a domain category.

        Args:
            tree_data: Current tree data including user prompt
            inputs: Tool inputs (unused for router)
            base_lm: Base language model for classification
            complex_lm: Complex language model (unused)
            client_manager: Client manager (unused)

        Yields:
            Status updates and classification result
        """
        if self.logger:
            self.logger.debug("Domain Router called!")
            self.logger.debug(
                "User prompt preview (chars=%s): %s",
                len(tree_data.user_prompt),
                tree_data.user_prompt[:200],
            )

        yield Status(
            "Analyzing query to determine if specialized knowledge is needed..."
        )

        # Get custom agents from environment (if any)
        custom_agents_info = tree_data.environment.hidden_environment.get(
            "custom_agents", {}
        )
        custom_agent_names = custom_agents_info.get("names", [])
        custom_agent_descriptions = custom_agents_info.get("descriptions", {})

        if self.logger:
            self.logger.debug(
                "Custom agents discovered: %s",
                {
                    "count": len(custom_agent_names),
                    "names": custom_agent_names,
                },
            )

        # Create dynamic prompt signature that includes custom agents
        DynamicPrompt = create_domain_router_prompt(
            custom_agent_names=custom_agent_names,
            custom_agent_descriptions=custom_agent_descriptions,
        )

        if self.logger:
            self.logger.debug(
                "Dynamic prompt signature ready: %s", DynamicPrompt.__name__
            )

        # Create classifier using ElysiaChainOfThought with dynamic prompt
        classifier = ElysiaChainOfThought(
            DynamicPrompt,
            tree_data=tree_data,
            reasoning=False,
            impossible=False,
            environment=False,
            tasks_completed=False,
            message_update=False,
        )

        # Build available domains list with custom agents
        valid_domains = ["not-related"] + custom_agent_names

        if self.logger and len(custom_agent_names) > 0:
            self.logger.debug(
                f"Router aware of {len(custom_agent_names)} custom agent(s): {custom_agent_names}"
            )

        # Perform classification
        try:
            self.logger.debug("Invoking domain classifier via base LM")
            classification = await classifier.aforward(
                lm=base_lm,
                user_prompt=tree_data.user_prompt,
            )

            domain = classification.domain.lower().strip()
            reasoning = classification.reasoning.strip()
            confidence = classification.confidence.lower().strip()

            if self.logger:
                self.logger.debug(f"Classification result: {domain}")
                self.logger.debug(f"Reasoning: {reasoning}")
                self.logger.debug(f"Confidence: {confidence}")

            # Normalize domain value to ensure consistency
            # Check if it matches any valid domain (case-insensitive)
            domain_found = False
            for valid_domain in valid_domains:
                if domain == valid_domain.lower():
                    domain = valid_domain
                    domain_found = True
                    break

            if not domain_found:
                if self.logger:
                    self.logger.warning(
                        f"Invalid domain '{domain}' returned by classifier. Defaulting to 'not-related'."
                    )
                domain = "not-related"

            # Store classification in hidden_environment for domain agents to access
            classification_payload = {
                "domain": domain,
                "reasoning": reasoning,
                "confidence": confidence,
            }
            tree_data.environment.hidden_environment["domain_classification"] = (
                classification_payload
            )

            if self.logger:
                self.logger.debug(
                    "Stored classification in hidden_environment: %s",
                    classification_payload,
                )

            # Yield user-facing response about classification
            if domain != "not-related":
                yield Response(
                    text=f"Routing to specialized agent: {domain.replace('-', ' ').replace('_', ' ')}..."
                )
            else:
                yield Response(text="Processing your query with general tools...")

            # Yield classification result
            yield DomainClassification(
                domain=domain,
                reasoning=reasoning,
                confidence=confidence,
            )

            if self.logger:
                self.logger.debug("Domain Router completed successfully!")

        except Exception as e:
            if self.logger:
                self.logger.exception("Error in domain classification")

            # On error, default to not-related and proceed with general processing
            error_payload = {
                "domain": "not-related",
                "reasoning": f"Classification failed: {str(e)}",
                "confidence": "low",
            }
            tree_data.environment.hidden_environment["domain_classification"] = (
                error_payload
            )

            yield Response(text="Proceeding with general processing...")

            yield DomainClassification(
                domain="not-related",
                reasoning=f"Classification error: {str(e)}",
                confidence="low",
            )

            if self.logger:
                self.logger.debug(
                    "Stored fallback classification after error: %s",
                    error_payload,
                )
