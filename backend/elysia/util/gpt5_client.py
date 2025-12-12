# ABOUTME: Custom client for OpenAI GPT-5 using the Responses API
# ABOUTME: Extends dspy.BaseLM to provide proper integration with DSPy framework

import logging
from typing import Any, Literal

import dspy
from openai import AsyncOpenAI, OpenAI

logger = logging.getLogger(__name__)


class GPT5ResponsesClient(dspy.BaseLM):
    """
    Custom client for GPT-5 models using OpenAI's Responses API.

    This client extends dspy.BaseLM to properly integrate with the DSPy framework
    while using the /v1/responses endpoint instead of /v1/chat/completions. This enables:
    - Reasoning effort control (minimal, low, medium, high)
    - Verbosity control (low, medium, high)
    - Full 400K context window optimization

    Args:
        model (str): The GPT-5 model to use (e.g., "gpt-5", "gpt-5-mini", "gpt-5-nano")
        reasoning_effort (str): Controls reasoning depth - "minimal", "low", "medium", or "high"
        text_verbosity (str): Controls output verbosity - "low", "medium", or "high"
        max_tokens (int): Maximum output tokens (default: 4096)
        temperature (float): Temperature parameter (default: 0.0)
        api_key (str | None): OpenAI API key (defaults to OPENAI_API_KEY env var)
        api_base (str | None): Custom API base URL (optional)
        cache (bool): Whether to enable caching (default: True)
        use_previous_response_id (bool): Whether to use previous_response_id for chain of thought.
            Default: False. Should remain False when using Elysia/DSPy since they already manage
            conversation history explicitly. Setting to True will cause context duplication and
            may exceed context limits.
        **kwargs: Additional parameters passed to BaseLM
    """

    def __init__(
        self,
        model: str,
        reasoning_effort: Literal["minimal", "low", "medium", "high"] = "medium",
        text_verbosity: Literal["low", "medium", "high"] = "medium",
        max_tokens: int = 4096,
        temperature: float = 0.0,
        api_key: str | None = None,
        api_base: str | None = None,
        cache: bool = True,
        use_previous_response_id: bool = False,  # Disabled by default to avoid context duplication
        **kwargs: Any,
    ):
        # Initialize BaseLM with model_type="responses" to use DSPy's response processor
        super().__init__(
            model=model,
            model_type="responses",
            temperature=temperature,
            max_tokens=max_tokens,
            cache=cache,
            **kwargs,
        )

        # Store Responses API-specific parameters
        self.reasoning_effort = reasoning_effort
        self.text_verbosity = text_verbosity
        self.use_previous_response_id = use_previous_response_id

        # Update kwargs with Responses API parameters
        self.kwargs.update(
            {
                "reasoning_effort": reasoning_effort,
                "text_verbosity": text_verbosity,
            }
        )

        # Initialize OpenAI clients
        client_kwargs: dict[str, Any] = {}
        if api_key:
            client_kwargs["api_key"] = api_key
        if api_base:
            client_kwargs["base_url"] = api_base

        self.client = OpenAI(**client_kwargs)
        self.async_client = AsyncOpenAI(**client_kwargs)

        # Store conversation state for previous_response_id (chain of thought)
        # NOTE: This is disabled by default because Elysia/DSPy already manages
        # conversation history explicitly by passing it in each request.
        # Using previous_response_id would duplicate the context and cause
        # context_length_exceeded errors.
        self.previous_response_id: str | None = None

    def _convert_messages_to_input(self, messages: list[dict[str, str]]) -> str:
        """
        Convert dspy-style messages to a single input string for Responses API.

        The Responses API uses 'input' instead of 'messages' array.
        We concatenate all messages into a single input string.
        """
        if not messages:
            return ""

        input_parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                input_parts.append(f"System: {content}")
            elif role == "user":
                input_parts.append(f"User: {content}")
            elif role == "assistant":
                input_parts.append(f"Assistant: {content}")

        combined = "\n\n".join(input_parts)
        logger.debug(
            "Combined %s chat messages into GPT-5 input (chars=%s)",
            len(messages),
            len(combined),
        )
        return combined

    def _prepare_request_params(self, input_text: str, **kwargs: Any) -> dict[str, Any]:
        """
        Prepare request parameters for the Responses API.

        Args:
            input_text (str): The input text to send to the model
            **kwargs: Additional parameters to pass to responses.create()

        Returns:
            dict: Request parameters for the Responses API
        """
        request_params: dict[str, Any] = {
            "model": self.model,
            "input": input_text,
            "reasoning": {"effort": self.reasoning_effort},
            "text": {"verbosity": self.text_verbosity},
            "max_output_tokens": self.kwargs.get("max_tokens", 4096),
        }

        # Add previous_response_id if available AND enabled for chain of thought
        # NOTE: This is disabled by default to avoid context duplication.
        # Elysia/DSPy already includes conversation history in each request.
        if self.use_previous_response_id and self.previous_response_id:
            request_params["previous_response_id"] = self.previous_response_id

        # Merge any additional kwargs (excluding internal DSPy params)
        filtered_kwargs = {
            k: v
            for k, v in kwargs.items()
            if k not in ["temperature", "max_tokens", "cache"]
        }
        request_params.update(filtered_kwargs)

        logger.debug(
            "Prepared GPT-5 request (model=%s, reasoning=%s, verbosity=%s, input_chars=%s, max_output_tokens=%s)",
            self.model,
            self.reasoning_effort,
            self.text_verbosity,
            len(input_text),
            request_params["max_output_tokens"],
        )

        return request_params

    def forward(
        self,
        prompt: str | None = None,
        messages: list[dict[str, str]] | None = None,
        **kwargs: Any,
    ) -> Any:
        """
        Synchronous forward pass for GPT-5 using Responses API.

        This method is called by BaseLM's __call__ method. It returns the raw
        OpenAI response object, which BaseLM will process and add to history.

        Args:
            prompt (str | None): Direct prompt string
            messages (list | None): List of message dicts with 'role' and 'content'
            **kwargs: Additional parameters for the API call

        Returns:
            OpenAI Response object (BaseLM will process this)
        """
        # Convert input to the format expected by Responses API
        if messages:
            input_text = self._convert_messages_to_input(messages)
        elif prompt:
            input_text = prompt
        else:
            raise ValueError("Either 'prompt' or 'messages' must be provided")

        # Prepare request parameters
        request_params = self._prepare_request_params(input_text, **kwargs)

        # Make the API call
        logger.info(
            "Calling GPT-5 Responses API (model=%s, input_chars=%s)",
            self.model,
            len(input_text),
        )
        response = self.client.responses.create(**request_params)

        # Store response_id for future requests (chain of thought)
        # Only store if the feature is enabled
        if self.use_previous_response_id and hasattr(response, "id"):
            self.previous_response_id = response.id

        # Calculate and attach cost to response for BaseLM history tracking
        if hasattr(response, "usage"):
            usage_obj = response.usage
            input_tokens = getattr(usage_obj, "input_tokens", 0)
            output_tokens = getattr(usage_obj, "output_tokens", 0)
            reasoning_tokens = getattr(usage_obj, "reasoning_tokens", 0)

            # GPT-5 pricing: $15.00 input / $120.00 output per 1M tokens
            cost = (input_tokens + reasoning_tokens) * 15.0 / 1_000_000
            cost += output_tokens * 120.0 / 1_000_000

            # Attach cost to response for BaseLM to track
            if not hasattr(response, "_hidden_params"):
                response._hidden_params = {}
            response._hidden_params["response_cost"] = cost

            logger.info(
                "GPT-5 sync response tokens: in=%s reason=%s out=%s cost=$%.4f",
                input_tokens,
                reasoning_tokens,
                output_tokens,
                cost,
            )

        # Return raw response - BaseLM will process it and manage history
        return response

    async def aforward(
        self,
        prompt: str | None = None,
        messages: list[dict[str, str]] | None = None,
        **kwargs: Any,
    ) -> Any:
        """
        Asynchronous forward pass for GPT-5 using Responses API.

        This method is called by BaseLM's acall method. It returns the raw
        OpenAI response object, which BaseLM will process and add to history.

        Args:
            prompt (str | None): Direct prompt string
            messages (list | None): List of message dicts with 'role' and 'content'
            **kwargs: Additional parameters for the API call

        Returns:
            OpenAI Response object (BaseLM will process this)
        """
        # Convert input to the format expected by Responses API
        if messages:
            input_text = self._convert_messages_to_input(messages)
        elif prompt:
            input_text = prompt
        else:
            raise ValueError("Either 'prompt' or 'messages' must be provided")

        # Prepare request parameters
        request_params = self._prepare_request_params(input_text, **kwargs)

        # Make the async API call
        logger.info(
            "Calling GPT-5 Responses API (async) model=%s input_chars=%s",
            self.model,
            len(input_text),
        )
        response = await self.async_client.responses.create(**request_params)

        # Store response_id for future requests (chain of thought)
        # Only store if the feature is enabled
        if self.use_previous_response_id and hasattr(response, "id"):
            self.previous_response_id = response.id

        # Calculate and attach cost to response for BaseLM history tracking
        if hasattr(response, "usage"):
            usage_obj = response.usage
            input_tokens = getattr(usage_obj, "input_tokens", 0)
            output_tokens = getattr(usage_obj, "output_tokens", 0)
            reasoning_tokens = getattr(usage_obj, "reasoning_tokens", 0)

            # GPT-5 pricing: $15.00 input / $120.00 output per 1M tokens
            cost = (input_tokens + reasoning_tokens) * 15.0 / 1_000_000
            cost += output_tokens * 120.0 / 1_000_000

            # Attach cost to response for BaseLM to track
            if not hasattr(response, "_hidden_params"):
                response._hidden_params = {}
            response._hidden_params["response_cost"] = cost

            logger.info(
                "GPT-5 async response tokens: in=%s reason=%s out=%s cost=$%.4f",
                input_tokens,
                reasoning_tokens,
                output_tokens,
                cost,
            )

        # Return raw response - BaseLM will process it and manage history
        return response

    def reset_conversation(self) -> None:
        """
        Reset the conversation state, clearing previous_response_id.

        Use this when starting a new conversation to ensure chain of thought
        doesn't carry over from previous interactions.

        NOTE: By default, previous_response_id is disabled (use_previous_response_id=False)
        to avoid context duplication with Elysia's conversation management.
        """
        logger.debug(
            "Resetting GPT-5 conversation state (previous_response_id cleared)"
        )
        self.previous_response_id = None

    def __repr__(self) -> str:
        return (
            f"GPT5ResponsesClient(model='{self.model}', "
            f"reasoning_effort='{self.reasoning_effort}', "
            f"text_verbosity='{self.text_verbosity}')"
        )
