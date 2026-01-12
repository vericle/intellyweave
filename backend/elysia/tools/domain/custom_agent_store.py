# ABOUTME: Storage layer for custom user-created agents
# ABOUTME: Handles Weaviate collection management and CRUD operations for custom agents

import uuid
from datetime import datetime
from logging import Logger
from typing import Any, cast

import dspy
import weaviate.classes.config as wc
from weaviate.classes.query import Filter
from weaviate.util import generate_uuid5

from elysia.util.client import ClientManager

CUSTOM_AGENTS_COLLECTION = "ELYSIA_CUSTOM_AGENTS__"
REMOTE_AGENT_PREFIX = "remote:"

_REMOTE_AGENT_CREATED_DATE = "2025-01-01T00:00:00Z"

REMOTE_AGENTS: list[dict[str, Any]] = []

# REMOTE_AGENTS: list[dict[str, Any]] = [
#     {
#         "agent_id": f"{REMOTE_AGENT_PREFIX}query",
#         "agent_name": "Query Agent",
#         "system_prompt": (
#             "Specialized agent that executes natural language"
#             " data questions over IntellyWeave's indexed collections using query orchestration."
#         ),
#         "document_id": None,
#         "user_id": "system",
#         "created_date": _REMOTE_AGENT_CREATED_DATE,
#         "agent_description": (
#             "Query Agent for semantic search, aggregation, and answer generation"
#             " across indexed intelligence artifacts."
#         ),
#         "is_read_only": True,
#         "source": "weaviate_remote",
#         "capabilities": ["question_answering", "semantic_search", "aggregation"],
#     },
#     {
#         "agent_id": f"{REMOTE_AGENT_PREFIX}transformation",
#         "agent_name": "Transformation Agent",
#         "system_prompt": (
#             "Transformation Agent that enhances documents by generating derived"
#             " data, summaries, or structured fields prior to ingestion."
#         ),
#         "document_id": None,
#         "user_id": "system",
#         "created_date": _REMOTE_AGENT_CREATED_DATE,
#         "agent_description": (
#             "Transformation pipeline for cleansing, summarizing, and enriching uploaded"
#             " intelligence content on demand."
#         ),
#         "is_read_only": True,
#         "source": "weaviate_remote",
#         "capabilities": ["data_cleaning", "summarization", "structure_enrichment"],
#     },
#     {
#         "agent_id": f"{REMOTE_AGENT_PREFIX}personalization",
#         "agent_name": "Personalization Agent",
#         "system_prompt": (
#             "Personalization service that tailors answers based on stored personas and"
#             " conversation context, similar to Weaviate's Personalization Agent."
#         ),
#         "document_id": None,
#         "user_id": "system",
#         "created_date": _REMOTE_AGENT_CREATED_DATE,
#         "agent_description": (
#             "Persona-aware response layer that adapts tone, detail, and evidence selection"
#             " to the requesting analyst."
#         ),
#         "is_read_only": True,
#         "source": "weaviate_remote",
#         "capabilities": ["persona_alignment", "intent_routing"],
#     },
# ]


def get_remote_agents() -> list[dict[str, Any]]:
    """Return metadata for read-only remote Weaviate agents."""
    return [agent.copy() for agent in REMOTE_AGENTS]


def is_remote_agent(agent_id: str) -> bool:
    """Check whether the given agent id belongs to a remote Weaviate agent."""
    return agent_id.startswith(REMOTE_AGENT_PREFIX)


class AgentDescriptionGenerator(dspy.Signature):
    """
    Generate a concise agent description suitable for query routing.

    The description should capture what topics/domains the agent handles
    based on the system prompt, making it easy for the router to determine
    when to use this agent.
    """

    system_prompt = dspy.InputField(
        desc="The full system prompt that defines the agent's behavior and knowledge domain"
    )

    agent_description = dspy.OutputField(
        desc="A concise 1-2 sentence description of what queries this agent can handle, suitable for routing decisions"
    )


async def create_custom_agents_collection(
    client_manager: ClientManager,
    logger: Logger | None = None,
) -> None:
    """
    Create the ELYSIA_CUSTOM_AGENTS__ collection if it doesn't exist.

    Args:
        client_manager: Client manager for Weaviate access
        logger: Optional logger for debug output
    """
    async with client_manager.connect_to_async_client() as client:
        if await client.collections.exists(CUSTOM_AGENTS_COLLECTION):
            if logger:
                logger.debug(f"Collection '{CUSTOM_AGENTS_COLLECTION}' already exists")
            return

        await client.collections.create(
            name=CUSTOM_AGENTS_COLLECTION,
            vectorizer_config=wc.Configure.Vectorizer.none(),
            inverted_index_config=wc.Configure.inverted_index(index_timestamps=True),
            properties=[
                wc.Property(
                    name="agent_id",
                    data_type=wc.DataType.TEXT,
                    description="Unique identifier for the custom agent",
                ),
                wc.Property(
                    name="agent_name",
                    data_type=wc.DataType.TEXT,
                    description="Human-readable name for the agent",
                ),
                wc.Property(
                    name="system_prompt",
                    data_type=wc.DataType.TEXT,
                    description="The system prompt that defines agent behavior",
                ),
                wc.Property(
                    name="document_id",
                    data_type=wc.DataType.TEXT,
                    description="UUID of the uploaded document serving as knowledge base",
                ),
                wc.Property(
                    name="user_id",
                    data_type=wc.DataType.TEXT,
                    description="ID of the user who created this agent",
                ),
                wc.Property(
                    name="created_date",
                    data_type=wc.DataType.DATE,
                    description="Timestamp when the agent was created",
                ),
                wc.Property(
                    name="agent_description",
                    data_type=wc.DataType.TEXT,
                    description="Auto-generated description for routing decisions",
                ),
            ],
        )

        if logger:
            logger.info(
                f"Created collection '{CUSTOM_AGENTS_COLLECTION}' for custom agents"
            )


async def generate_agent_description(
    system_prompt: str,
    lm: dspy.LM,
    logger: Logger | None = None,
) -> str:
    """
    Use LLM to generate a routing-friendly description from system prompt.

    Args:
        system_prompt: The full system prompt for the agent
        lm: Language model to use for generation
        logger: Optional logger for debug output

    Returns:
        Generated agent description suitable for routing
    """
    try:
        generator = dspy.ChainOfThought(AgentDescriptionGenerator)
        with dspy.context(lm=lm):
            result = generator(system_prompt=system_prompt)

        description = result.agent_description.strip()

        if logger:
            logger.debug(f"Generated agent description: {description}")

        return description

    except Exception as e:
        if logger:
            logger.error(
                f"Error generating agent description: {str(e)}. "
                "Using system prompt excerpt as fallback."
            )
        # Fallback: use first 200 chars of system prompt
        return system_prompt[:200].strip() + "..."


async def store_custom_agent(
    agent_name: str,
    system_prompt: str,
    document_id: str,
    user_id: str,
    agent_description: str,
    client_manager: ClientManager,
    logger: Logger | None = None,
) -> dict[str, Any]:
    """
    Store a custom agent definition in Weaviate.

    Args:
        agent_name: Human-readable name for the agent
        system_prompt: The system prompt defining agent behavior
        document_id: UUID of the document serving as knowledge base
        user_id: ID of the user creating the agent
        agent_description: Description for routing (pre-generated)
        client_manager: Client manager for Weaviate access
        logger: Optional logger for debug output

    Returns:
        Dictionary containing agent metadata including agent_id
    """
    # Ensure collection exists
    await create_custom_agents_collection(client_manager, logger)

    agent_id = str(uuid.uuid4())
    created_date = datetime.now()

    # Data for Weaviate storage (with datetime object)
    weaviate_data = {
        "agent_id": agent_id,
        "agent_name": agent_name,
        "system_prompt": system_prompt,
        "document_id": document_id,
        "user_id": user_id,
        "created_date": created_date,
        "agent_description": agent_description,
    }

    async with client_manager.connect_to_async_client() as client:
        collection = client.collections.get(CUSTOM_AGENTS_COLLECTION)

        # Use agent_id to generate consistent UUID for Weaviate
        weaviate_uuid = generate_uuid5(agent_id)

        await collection.data.insert(
            uuid=weaviate_uuid,
            properties=weaviate_data,
        )

    if logger:
        logger.info(
            f"Stored custom agent '{agent_name}' (ID: {agent_id}) for user {user_id}"
        )

    # Return data with ISO format date string for JSON serialization
    return {
        "agent_id": agent_id,
        "agent_name": agent_name,
        "system_prompt": system_prompt,
        "document_id": document_id,
        "user_id": user_id,
        "created_date": created_date.isoformat(),
        "agent_description": agent_description,
    }


async def load_user_custom_agents(
    user_id: str,
    client_manager: ClientManager,
    logger: Logger | None = None,
) -> list[dict[str, Any]]:
    """
    Load all custom agents for a specific user.

    Args:
        user_id: ID of the user whose agents to load
        client_manager: Client manager for Weaviate access
        logger: Optional logger for debug output

    Returns:
        List of agent metadata dictionaries
    """
    async with client_manager.connect_to_async_client() as client:
        # Check if collection exists
        if not await client.collections.exists(CUSTOM_AGENTS_COLLECTION):
            if logger:
                logger.debug(
                    f"Collection '{CUSTOM_AGENTS_COLLECTION}' does not exist. "
                    "No custom agents available."
                )
            return get_remote_agents()

        collection = client.collections.get(CUSTOM_AGENTS_COLLECTION)

        # Query for all agents belonging to this user
        response = await collection.query.fetch_objects(
            filters=Filter.by_property("user_id").equal(user_id),
            limit=100,  # Reasonable limit for custom agents per user
        )

        agents = []
        for obj in response.objects:
            agent_dict = dict(obj.properties)
            agent_dict["uuid"] = str(obj.uuid)

            # Convert datetime to ISO format string for JSON serialization
            if "created_date" in agent_dict and isinstance(
                agent_dict["created_date"], datetime
            ):
                agent_dict["created_date"] = agent_dict["created_date"].isoformat()

            agents.append(agent_dict)

        remote_agents = get_remote_agents()
        combined_agents = agents + remote_agents

        if logger:
            logger.debug(
                f"Loaded {len(agents)} custom agent(s) and {len(remote_agents)} remote agent(s) for user {user_id}"
            )

        return combined_agents


async def delete_custom_agent(
    agent_id: str,
    user_id: str,
    client_manager: ClientManager,
    logger: Logger | None = None,
) -> bool:
    """
    Delete a custom agent.

    Args:
        agent_id: ID of the agent to delete
        user_id: ID of the user (for authorization check)
        client_manager: Client manager for Weaviate access
        logger: Optional logger for debug output

    Returns:
        True if agent was deleted, False if not found or unauthorized
    """
    if is_remote_agent(agent_id):
        if logger:
            logger.warning(
                "Attempt to delete read-only remote agent %s by user %s",
                agent_id,
                user_id,
            )
        return False

    async with client_manager.connect_to_async_client() as client:
        if not await client.collections.exists(CUSTOM_AGENTS_COLLECTION):
            if logger:
                logger.warning(
                    f"Collection '{CUSTOM_AGENTS_COLLECTION}' does not exist"
                )
            return False

        collection = client.collections.get(CUSTOM_AGENTS_COLLECTION)
        weaviate_uuid = generate_uuid5(agent_id)

        # First check if agent exists and belongs to user
        obj = await collection.query.fetch_object_by_id(weaviate_uuid)

        if obj is None:
            if logger:
                logger.warning(f"Agent {agent_id} not found")
            return False

        if obj.properties.get("user_id") != user_id:
            if logger:
                logger.warning(
                    f"User {user_id} not authorized to delete agent {agent_id}"
                )
            return False

        # Delete the agent
        await collection.data.delete_by_id(weaviate_uuid)

        if logger:
            logger.info(f"Deleted custom agent {agent_id} for user {user_id}")

        return True


async def update_custom_agent(
    agent_id: str,
    user_id: str,
    agent_name: str,
    system_prompt: str,
    client_manager: ClientManager,
    settings: Any,
    logger: Logger | None = None,
) -> dict[str, Any] | None:
    """
    Update a custom agent's name and system prompt.

    Args:
        agent_id: ID of the agent to update
        user_id: ID of the user (for authorization check)
        agent_name: New name for the agent
        system_prompt: New system prompt
        client_manager: Client manager for Weaviate access
        settings: Settings object for LLM configuration
        logger: Optional logger for debug output

    Returns:
        Updated agent metadata dictionary, or None if not found/unauthorized
    """
    if is_remote_agent(agent_id):
        if logger:
            logger.warning(
                "Attempt to update read-only remote agent %s by user %s",
                agent_id,
                user_id,
            )
        return None

    async with client_manager.connect_to_async_client() as client:
        if not await client.collections.exists(CUSTOM_AGENTS_COLLECTION):
            if logger:
                logger.warning(
                    f"Collection '{CUSTOM_AGENTS_COLLECTION}' does not exist"
                )
            return None

        collection = client.collections.get(CUSTOM_AGENTS_COLLECTION)
        weaviate_uuid = generate_uuid5(agent_id)

        # First check if agent exists and belongs to user
        obj = await collection.query.fetch_object_by_id(weaviate_uuid)

        if obj is None:
            if logger:
                logger.warning(f"Agent {agent_id} not found")
            return None

        if obj.properties.get("user_id") != user_id:
            if logger:
                logger.warning(
                    f"User {user_id} not authorized to update agent {agent_id}"
                )
            return None

        # Generate new agent description from updated system prompt
        from elysia.config import load_base_lm

        base_lm = cast(dspy.LM, load_base_lm(settings))
        agent_description = await generate_agent_description(
            system_prompt=system_prompt,
            lm=base_lm,
            logger=logger,
        )

        # Update the agent
        updated_data = {
            "agent_id": agent_id,
            "agent_name": agent_name,
            "system_prompt": system_prompt,
            "document_id": obj.properties.get("document_id"),
            "user_id": user_id,
            "created_date": obj.properties.get("created_date"),
            "agent_description": agent_description,
        }

        await collection.data.update(
            uuid=weaviate_uuid,
            properties=updated_data,
        )

        if logger:
            logger.info(
                f"Updated custom agent '{agent_name}' (ID: {agent_id}) for user {user_id}"
            )

        # Return data with ISO format date string for JSON serialization
        created_date = obj.properties.get("created_date")
        if isinstance(created_date, datetime):
            created_date = created_date.isoformat()

        return {
            "agent_id": agent_id,
            "agent_name": agent_name,
            "system_prompt": system_prompt,
            "document_id": obj.properties.get("document_id"),
            "user_id": user_id,
            "created_date": created_date,
            "agent_description": agent_description,
        }
