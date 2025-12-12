# ABOUTME: Registry for managing and loading custom user agents
# ABOUTME: Handles dynamic agent discovery and instantiation for tree integration

import logging
from logging import Logger
from typing import Any

from elysia.agents import (
    GeospatialTransformationTool,
    PersonalizationAgent,
    PersonalizationTool,
    QueryExtractorTool,
)
from elysia.objects import Tool
from elysia.tools.domain.custom_agent_factory import CustomAgentFactory
from elysia.tools.domain.custom_agent_store import load_user_custom_agents
from elysia.util.client import ClientManager

module_logger = logging.getLogger(__name__)


class CustomAgentRegistry:
    """
    Registry for managing custom agents.

    Loads custom agents from Weaviate and instantiates them as Tool objects
    for integration with the decision tree.

    This is designed to be used per-tree-instance, not as a global singleton,
    to ensure proper user-scoping and avoid cross-user contamination.
    """

    def __init__(self, logger: Logger | None = None):
        """
        Initialize an empty agent registry.

        Args:
            logger: Optional logger for debug output
        """
        self.agents: list[Tool] = []
        self.agent_metadata: list[dict[str, Any]] = []
        self.logger = logger or module_logger
        self._loaded_user_id: str | None = None

    async def load_custom_agents(
        self,
        user_id: str,
        client_manager: ClientManager,
        collection_name: str = "ELYSIA_CHUNKED_elysia_uploaded_documents__",
    ) -> list[Tool]:
        """
        Load all custom agents for a specific user.

        Args:
            user_id: ID of the user whose agents to load
            client_manager: Client manager for Weaviate access
            collection_name: Collection containing document chunks (default: chunked documents)

        Returns:
            List of instantiated custom agent Tool objects
        """
        if self.logger:
            self.logger.debug(
                "Loading custom agents for user %s (collection=%s)",
                user_id,
                collection_name,
            )

        # Load agent metadata from Weaviate
        agent_metadata_list = await load_user_custom_agents(
            user_id=user_id,
            client_manager=client_manager,
            logger=self.logger,
        )

        if self.logger:
            self.logger.info(
                "Retrieved %s custom agent metadata entries for user %s",
                len(agent_metadata_list),
                user_id,
            )

        # Store metadata
        self.agent_metadata = agent_metadata_list
        self._loaded_user_id = user_id

        # Instantiate agent Tools using factory
        self.agents = []
        for metadata in agent_metadata_list:
            try:
                agent_tool = CustomAgentFactory.create_agent(
                    agent_metadata=metadata,
                    collection_name=collection_name,
                    logger=self.logger,
                )
                self.agents.append(agent_tool)

                if self.logger:
                    self.logger.debug(
                        f"Loaded custom agent '{metadata['agent_name']}' "
                        f"(ID: {metadata['agent_id']})"
                    )

            except Exception as e:
                if self.logger:
                    self.logger.exception(
                        "Failed to load custom agent %s",
                        metadata.get("agent_name", "unknown"),
                    )
                # Continue loading other agents even if one fails

        # Add system specialized agents (Option A: Decision Tree Tools)
        try:
            system_agents = [
                QueryExtractorTool(logger=self.logger),
                GeospatialTransformationTool(logger=self.logger),
                PersonalizationTool(logger=self.logger),
            ]

            for agent in system_agents:
                self.agents.append(agent)
                # Add metadata so router knows about them
                self.agent_metadata.append(
                    {
                        "agent_id": agent.name,
                        "agent_name": agent.name,
                        "agent_description": agent.description,
                        "system_prompt": "System Agent",  # Placeholder
                        "document_id": "system",
                        "user_id": user_id,
                        "created_date": None,
                    }
                )

                if self.logger:
                    self.logger.debug(
                        "Loaded system specialized agent: %s (description=%s)",
                        agent.name,
                        agent.description,
                    )

        except Exception as e:
            if self.logger:
                self.logger.exception("Failed to load system specialized agents")

        # Add router-accessible agents (Option B: Custom User Agents)
        try:
            router_accessible_agents = [
                PersonalizationAgent(logger=self.logger),
            ]

            for agent in router_accessible_agents:
                self.agents.append(agent)
                # Add metadata with proper agent description for router
                self.agent_metadata.append(
                    {
                        "agent_id": agent.name,
                        "agent_name": agent.name,
                        "agent_description": agent.description,
                        "system_prompt": "Router-accessible system agent for personalization",
                        "document_id": "system",
                        "user_id": user_id,
                        "created_date": None,
                    }
                )

                if self.logger:
                    self.logger.debug(
                        "Loaded router-accessible agent: %s (description=%s)",
                        agent.name,
                        agent.description,
                    )

        except Exception as e:
            if self.logger:
                self.logger.exception("Failed to load router-accessible agents")

        if self.logger:
            self.logger.info(
                "Loaded %s total agent(s) (custom=%s, system=%s) for user %s",
                len(self.agents),
                len(agent_metadata_list),
                len(self.agents) - len(agent_metadata_list),
                user_id,
            )

        return self.agents

    def get_agents(self) -> list[Tool]:
        """
        Get the list of loaded custom agent Tools.

        Returns:
            List of custom agent Tool instances
        """
        return self.agents

    def get_agent_metadata(self) -> list[dict[str, Any]]:
        """
        Get the metadata for all loaded agents.

        Returns:
            List of agent metadata dictionaries
        """
        return self.agent_metadata

    def get_agent_names(self) -> list[str]:
        """
        Get names of all loaded custom agents.

        Useful for extending the domain router's valid domain list.

        Returns:
            List of agent names
        """
        return [metadata["agent_name"] for metadata in self.agent_metadata]

    def get_agent_descriptions(self) -> dict[str, str]:
        """
        Get agent names mapped to their descriptions.

        Useful for dynamic router prompt construction.

        Returns:
            Dictionary mapping agent names to descriptions
        """
        return {
            metadata["agent_name"]: metadata["agent_description"]
            for metadata in self.agent_metadata
        }

    async def refresh(
        self,
        user_id: str,
        client_manager: ClientManager,
        collection_name: str = "ELYSIA_CHUNKED_elysia_uploaded_documents__",
    ) -> list[Tool]:
        """
        Refresh the agent registry by reloading from Weaviate.

        Useful if agents were added/modified after initial load.

        Args:
            user_id: ID of the user whose agents to load
            client_manager: Client manager for Weaviate access
            collection_name: Collection containing document chunks

        Returns:
            Updated list of custom agent Tool instances
        """
        if self.logger:
            self.logger.info("Refreshing custom agent registry for user %s", user_id)

        return await self.load_custom_agents(
            user_id=user_id,
            client_manager=client_manager,
            collection_name=collection_name,
        )

    def clear(self) -> None:
        """
        Clear all loaded agents from the registry.

        Useful for cleanup or when switching users.
        """
        previous_count = len(self.agents)
        self.agents = []
        self.agent_metadata = []
        self._loaded_user_id = None

        if self.logger:
            self.logger.info(
                "Cleared custom agent registry (removed %s agent(s))", previous_count
            )

    def is_loaded(self) -> bool:
        """
        Check if agents have been loaded.

        Returns:
            True if agents are loaded, False otherwise
        """
        return len(self.agents) > 0

    def get_loaded_user_id(self) -> str | None:
        """
        Get the user ID for which agents are currently loaded.

        Returns:
            User ID or None if no agents loaded
        """
        return self._loaded_user_id
