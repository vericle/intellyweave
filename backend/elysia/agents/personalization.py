# ABOUTME: Personalization Tool
# ABOUTME: Adjusts workflow and decision trees based on user intent and history

import json
from typing import Any, AsyncGenerator, Dict, List, Optional

import dspy

from elysia.api.core.log import logger as core_logger
from elysia.objects import Error, Result, Status, Tool
from elysia.tree.objects import TreeData
from elysia.util.client import ClientManager


class UserIntentSignature(dspy.Signature):
    """
    Analyze the user's query and profile to determine their specific intent and
    recommend configuration adjustments for the intelligence analysis workflow.
    """

    query: str = dspy.InputField(desc="The user's current query")
    user_profile: Dict[str, Any] = dspy.InputField(
        desc="User's historical preferences and role"
    )

    intent_category: str = dspy.OutputField(
        desc="Category of intent (e.g., 'historical_research', 'quick_intel', 'legal_analysis', 'geospatial_exploration')"
    )
    workflow_adjustments: Dict[str, Any] = dspy.OutputField(
        desc="Configuration parameters to adjust (e.g., {'use_deep_search': True, 'focus_domains': ['archives']})"
    )
    reasoning: str = dspy.OutputField(desc="Why these adjustments are recommended")


class UserProfileStore:
    """
    Interface for retrieving user profiles.
    """

    async def get(self, user_id: str) -> Dict[str, Any]:
        # Placeholder implementation
        # In production, fetch from database
        return {
            "user_id": user_id,
            "role": "intelligence_analyst",
            "preferences": {
                "default_depth": "comprehensive",
                "focus_areas": ["military", "geopolitics"],
            },
            "history_summary": "User frequently analyzes conflict zones in Eastern Europe.",
        }


class PersonalizationTool(Tool):
    """
    Personalization Tool.
    Role: Adjusts execution parameters based on user intent.
    Acts as a Router or Re-ranker before main execution.
    """

    def __init__(
        self,
        logger=None,
        user_profile_store: Optional[UserProfileStore] = None,
        **kwargs,
    ):
        self.logger = logger or core_logger
        self.profiles = user_profile_store or UserProfileStore()
        super().__init__(
            name="personalization_tool",
            description="Adjusts workflow and decision trees based on user intent and history. Use this at the start of a session to tailor the analysis parameters to the user's specific needs.",
            inputs={
                "query": {
                    "description": "The user's current query.",
                    "type": "string",
                    "required": True,
                },
                "user_id": {
                    "description": "The ID of the user.",
                    "type": "string",
                    "required": True,
                },
            },
            **kwargs,
        )

    async def __call__(
        self,
        tree_data: TreeData,
        inputs: Dict[str, Any],
        base_lm: dspy.LM,
        complex_lm: dspy.LM,
        client_manager: ClientManager,
        **kwargs,
    ) -> AsyncGenerator[Result | Status | Error, None]:
        """
        Analyze intent and return a workflow configuration.
        """
        query = inputs.get("query")
        user_id = inputs.get("user_id")

        if not query or not user_id:
            self._log_error(
                "personalization.validation_error",
                data={"has_query": bool(query), "has_user_id": bool(user_id)},
            )
            yield Error("Query and User ID are required for personalization.")
            return

        self._log_info(
            "personalization.start",
            data={"user_id": user_id, "query_preview": query[:200]},
        )
        yield Status(f"Personalizing workflow for user {user_id}...")

        self._log_debug(
            "personalization.optimize",
            data={"user_id": user_id, "query_length": len(query)},
        )

        # Initialize chain
        chain = dspy.ChainOfThought(UserIntentSignature)

        # 1. Fetch User Preferences
        try:
            profile = await self.profiles.get(user_id)
            self._log_debug(
                "personalization.profile_loaded",
                data={
                    "user_id": user_id,
                    "role": profile.get("role"),
                    "preference_keys": list(profile.get("preferences", {}).keys()),
                },
            )
        except Exception as e:
            self._log_error(
                "personalization.profile_error",
                data={"user_id": user_id, "error": str(e)},
            )
            yield Error(f"Failed to fetch user profile: {str(e)}")
            return

        # 2. Analyze Intent
        try:
            with dspy.settings.context(lm=base_lm):
                result = chain(query=query, user_profile=profile)
        except Exception as e:
            self._log_error(
                "personalization.intent_error",
                data={"user_id": user_id, "error": str(e)},
            )
            yield Error(f"LLM intent analysis failed: {str(e)}")
            return

        self._log_info(
            "personalization.intent_detected",
            data={
                "user_id": user_id,
                "intent": result.intent_category,
                "adjustments": result.workflow_adjustments,
            },
        )
        self._log_debug(
            "personalization.reasoning",
            data={"user_id": user_id, "reasoning": result.reasoning[:500]},
        )

        # 3. Construct Final Config
        # Merge default config with adjustments
        config = {
            "intent": result.intent_category,
            "reasoning": result.reasoning,
            "settings": result.workflow_adjustments,
        }
        self._log_debug(
            "personalization.output",
            data={"user_id": user_id, "settings_keys": list(config["settings"].keys())},
        )

        yield Result(
            objects=[config],
            name="workflow_configuration",
            metadata={"user_id": user_id, "intent": result.intent_category},
        )

    def _log_debug(self, message: str, data: Optional[dict] = None) -> None:
        self._emit_log("debug", message, data)

    def _log_info(self, message: str, data: Optional[dict] = None) -> None:
        self._emit_log("info", message, data)

    def _log_error(self, message: str, data: Optional[dict] = None) -> None:
        self._emit_log("error", message, data)

    def _emit_log(self, level: str, message: str, data: Optional[dict]) -> None:
        if not self.logger:
            return
        log_method = getattr(self.logger, level, None)
        if not log_method:
            return
        if data:
            log_method(f"{message} | data={self._serialize_payload(data)}")
        else:
            log_method(message)

    @staticmethod
    def _serialize_payload(payload: dict) -> str:
        try:
            return json.dumps(payload)
        except TypeError:
            return repr(payload)


class PersonalizationAgent(Tool):
    """
    Router-accessible Personalization Agent (Option B).

    This agent is selectable by the DomainRouter when queries involve
    workflow customization, user preference adaptation, or personalized
    intelligence analysis.
    """

    def __init__(
        self,
        logger=None,
        user_profile_store: Optional[UserProfileStore] = None,
        **kwargs,
    ):
        self.logger = logger or core_logger
        self.personalization_tool = PersonalizationTool(
            logger=self.logger, user_profile_store=user_profile_store
        )
        super().__init__(
            name="Personalization Agent",
            description="Tailors intelligence analysis workflows based on user preferences, role, and historical behavior. Use when queries involve customizing search depth, focus areas, or analytical approaches for specific user needs.",
            status="Personalizing workflow based on your preferences...",
            inputs={},
            end=True,
            **kwargs,
        )

    async def is_tool_available(
        self,
        tree_data: TreeData,
        base_lm: dspy.LM,
        complex_lm: dspy.LM,
        client_manager: ClientManager,
        **kwargs,
    ) -> bool:
        """
        Check if this agent should handle the current query.

        Available if router classified query as personalization-related domain.
        """
        classification = tree_data.environment.hidden_environment.get(
            "domain_classification", {}
        )

        classified_domain = classification.get("domain", "").lower()

        # Match various personalization-related domain names
        personalization_domains = [
            "personalization agent",
            "weaviate personalization agent",
            "personalization",
            "remote:personalization",
        ]

        return any(domain in classified_domain for domain in personalization_domains)

    async def __call__(
        self,
        tree_data: TreeData,
        inputs: Dict[str, Any],
        base_lm: dspy.LM,
        complex_lm: dspy.LM,
        client_manager: ClientManager,
        **kwargs,
    ) -> AsyncGenerator[Result | Status | Error, None]:
        """
        Execute personalization workflow.

        Delegates to PersonalizationTool with proper inputs.
        """
        self._log_debug(
            "personalization.agent_start",
            data={"user_prompt_preview": tree_data.user_prompt[:200]},
        )

        # Extract user_id from tree_data
        user_id = tree_data.environment.hidden_environment.get("user_id", "unknown")

        # Prepare inputs for PersonalizationTool
        tool_inputs = {
            "query": tree_data.user_prompt,
            "user_id": user_id,
        }

        # Delegate to PersonalizationTool
        async for output in self.personalization_tool(
            tree_data=tree_data,
            inputs=tool_inputs,
            base_lm=base_lm,
            complex_lm=complex_lm,
            client_manager=client_manager,
            **kwargs,
        ):
            yield output

    def _log_debug(self, message: str, data: Optional[dict] = None) -> None:
        self._emit_log("debug", message, data)

    def _emit_log(self, level: str, message: str, data: Optional[dict]) -> None:
        if not self.logger:
            return
        log_method = getattr(self.logger, level, None)
        if not log_method:
            return
        if data:
            try:
                serialized = json.dumps(data)
            except TypeError:
                serialized = repr(data)
            log_method(f"{message} | data={serialized}")
        else:
            log_method(message)
