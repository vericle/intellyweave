# ABOUTME: DSPy prompt templates for domain routing and specialized agents
# ABOUTME: Defines classification prompts and domain-specific response generation prompts

import logging

import dspy
from pydantic import Field

logger = logging.getLogger(__name__)


def create_domain_router_prompt(
    custom_agent_names: list[str] | None = None,
    custom_agent_descriptions: dict[str, str] | None = None,
) -> type[dspy.Signature]:
    """
    Dynamically create a DomainRouterPrompt signature that includes custom agents.

    Args:
        custom_agent_names: List of custom agent names to include as valid domains
        custom_agent_descriptions: Dictionary mapping agent names to their descriptions

    Returns:
        A DSPy Signature class configured with the appropriate domain options
    """
    custom_agent_names = custom_agent_names or []
    custom_agent_descriptions = custom_agent_descriptions or {}

    logger.info(
        "Building domain router prompt (custom_agents=%s)",
        len(custom_agent_names),
    )

    # Build domain list description
    domain_list_parts = []

    # Add custom agents to domain descriptions
    for agent_name in custom_agent_names:
        description = custom_agent_descriptions.get(
            agent_name, "Custom specialized agent"
        )
        domain_list_parts.append(f"- {agent_name}: {description}")

    if logger.isEnabledFor(logging.DEBUG) and custom_agent_names:
        logger.debug(
            "Custom agent descriptions available for router: %s",
            {
                name: custom_agent_descriptions.get(name, "Custom specialized agent")
                for name in custom_agent_names
            },
        )

    # Build valid domain values
    valid_domain_values = custom_agent_names + ["not-related"]
    valid_domains_str = ", ".join(f"'{d}'" for d in valid_domain_values)
    logger.debug("Valid router domains: %s", valid_domain_values)

    # Create appropriate wording based on whether custom agents exist
    if len(custom_agent_names) > 0:
        domain_list_parts.append(
            "- not-related: Query doesn't match any of the specialized agents above"
        )
        domain_list_str = "\n    ".join(domain_list_parts)
        docstring = f"""
    Classify user queries to route to appropriate specialized agents.

    Available specialized agents:
    {domain_list_str}

    Consider the intent and context of the query, not just keywords.
    Only classify as a specialized agent if the query clearly requires that agent's expertise.
    Otherwise, classify as 'not-related' for general processing.
    """
        domain_field_desc = (
            f"The classified domain. Must be exactly one of: {valid_domains_str}. "
            "Only choose a specialized agent if the query clearly requires that agent's specific expertise. "
            "Use 'not-related' for general queries."
        )
        logger.info(
            "Router prompt configured with %s specialized agent(s) + fallback domain",
            len(custom_agent_names),
        )
    else:
        # No custom agents - simple fallback
        docstring = """
    Classify user queries for processing.

    No specialized agents are currently available.
    All queries will be processed using general tools.
    """
        domain_field_desc = (
            "The domain classification. Must be 'not-related' since no specialized agents are available. "
            "All queries use general processing."
        )
        logger.info(
            "Router prompt configured without specialized agents (default only)"
        )

    class DynamicDomainRouterPrompt(dspy.Signature):
        __doc__ = docstring

        user_prompt: str = dspy.InputField(desc="The user's original query to classify")

        domain: str = dspy.OutputField(desc=domain_field_desc)

        reasoning: str = dspy.OutputField(
            desc=(
                "Brief explanation (1-2 sentences) of why this domain was chosen. "
                "Reference specific keywords or concepts from the query that indicate this domain."
            )
        )

        confidence: str = dspy.OutputField(
            desc=(
                "Confidence level in this classification. Must be one of: 'high', 'medium', or 'low'. "
                "Use 'high' when query clearly matches domain, 'medium' when partially related, 'low' when uncertain."
            )
        )

    logger.debug(
        "Domain router prompt signature created: %s", DynamicDomainRouterPrompt
    )
    return DynamicDomainRouterPrompt
