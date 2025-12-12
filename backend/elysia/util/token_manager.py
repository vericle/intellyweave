# ABOUTME: Token management utilities for tracking and limiting token usage in LLM requests
# ABOUTME: Provides token counting, context truncation, and rate limiting to prevent API errors

import asyncio
import logging
import time
from collections import deque
from typing import Any

import tiktoken


class TokenCounter:
    """
    Handles token counting for different models using tiktoken.
    Falls back to character-based estimation if tiktoken fails.
    """

    def __init__(self):
        self.encoders = {}
        self.logger = logging.getLogger("rich")

    def _get_encoder(self, model: str):
        """Get or create encoder for a specific model."""
        if model not in self.encoders:
            try:
                # Try to get encoding for the model
                if model.startswith("gpt-5") or model.startswith("gpt-3.5"):
                    encoding_name = "cl100k_base"
                elif model.startswith("claude"):
                    encoding_name = "cl100k_base"  # Claude uses similar tokenization
                elif model.startswith("gemini"):
                    encoding_name = "cl100k_base"  # Gemini approximation
                else:
                    encoding_name = "cl100k_base"  # Default fallback

                self.encoders[model] = tiktoken.get_encoding(encoding_name)
            except Exception as e:
                self.logger.warning(
                    f"Failed to load tiktoken encoder for {model}: {e}. Using character estimation."
                )
                self.encoders[model] = None

        return self.encoders[model]

    def count_tokens(self, text: str, model: str = "gpt-5") -> int:
        """
        Count tokens in text for a given model.
        Falls back to character-based estimation (chars/4) if tiktoken fails.
        """
        if not text:
            return 0

        encoder = self._get_encoder(model)

        if encoder is not None:
            try:
                return len(encoder.encode(str(text)))
            except Exception as e:
                self.logger.debug(f"Token encoding failed: {e}. Using estimation.")

        # Fallback: estimate ~4 characters per token
        return len(str(text)) // 4

    def count_messages_tokens(self, messages: list[dict], model: str = "gpt-5") -> int:
        """
        Count tokens in a list of messages (conversation format).
        Includes overhead for message formatting.
        """
        total_tokens = 0

        for message in messages:
            # Count tokens in role and content
            if "role" in message:
                total_tokens += self.count_tokens(message["role"], model)
            if "content" in message:
                total_tokens += self.count_tokens(str(message["content"]), model)

            # Add overhead for message formatting (approximately 4 tokens per message)
            total_tokens += 4

        # Add overhead for conversation formatting
        total_tokens += 3

        return total_tokens


class RateLimiter:
    """
    Token-based rate limiter with sliding window.
    Tracks token usage over time to prevent exceeding rate limits.
    """

    def __init__(
        self,
        tokens_per_minute: int = 30000,
        requests_per_minute: int = 500,
        window_seconds: int = 60,
    ):
        self.tokens_per_minute = tokens_per_minute
        self.requests_per_minute = requests_per_minute
        self.window_seconds = window_seconds

        # Use deque for efficient sliding window
        self.token_usage = deque()  # (timestamp, tokens)
        self.request_times = deque()  # timestamps

        self.logger = logging.getLogger("rich")

    def _clean_old_entries(self, current_time: float):
        """Remove entries older than the window."""
        cutoff_time = current_time - self.window_seconds

        while self.token_usage and self.token_usage[0][0] < cutoff_time:
            self.token_usage.popleft()

        while self.request_times and self.request_times[0] < cutoff_time:
            self.request_times.popleft()

    def get_current_usage(self) -> tuple[int, int]:
        """Get current token and request usage in the window."""
        current_time = time.time()
        self._clean_old_entries(current_time)

        total_tokens = sum(tokens for _, tokens in self.token_usage)
        total_requests = len(self.request_times)

        return total_tokens, total_requests

    def can_make_request(self, estimated_tokens: int) -> bool:
        """Check if a request can be made without exceeding limits."""
        current_tokens, current_requests = self.get_current_usage()

        # Check if adding this request would exceed limits
        would_exceed_tokens = (
            current_tokens + estimated_tokens
        ) > self.tokens_per_minute
        would_exceed_requests = (current_requests + 1) > self.requests_per_minute

        return not (would_exceed_tokens or would_exceed_requests)

    def wait_time(self, estimated_tokens: int) -> float:
        """Calculate how long to wait before making a request."""
        if self.can_make_request(estimated_tokens):
            return 0.0

        current_time = time.time()
        self._clean_old_entries(current_time)

        if not self.token_usage and not self.request_times:
            return 0.0

        # Find the earliest time we can make the request
        wait_for_tokens = 0.0
        wait_for_requests = 0.0

        # Check token limit
        if self.token_usage:
            total_tokens = sum(tokens for _, tokens in self.token_usage)
            if total_tokens + estimated_tokens > self.tokens_per_minute:
                # Wait until oldest token usage expires
                oldest_time = self.token_usage[0][0]
                wait_for_tokens = (oldest_time + self.window_seconds) - current_time

        # Check request limit
        if len(self.request_times) >= self.requests_per_minute:
            oldest_request = self.request_times[0]
            wait_for_requests = (oldest_request + self.window_seconds) - current_time

        return max(wait_for_tokens, wait_for_requests, 0.0)

    async def acquire(self, estimated_tokens: int):
        """
        Acquire permission to make a request.
        Waits if necessary to respect rate limits.
        """
        wait_time = self.wait_time(estimated_tokens)

        if wait_time > 0:
            self.logger.warning(
                f"Rate limit approaching. Waiting {wait_time:.2f} seconds before making request."
            )
            await asyncio.sleep(wait_time)

        # Record the request
        current_time = time.time()
        self.token_usage.append((current_time, estimated_tokens))
        self.request_times.append(current_time)

    def record_usage(self, actual_tokens: int):
        """
        Update the last request with actual token usage.
        Called after receiving the API response.
        """
        if self.token_usage:
            timestamp, _ = self.token_usage[-1]
            self.token_usage[-1] = (timestamp, actual_tokens)


class ContextTruncator:
    """
    Intelligently truncates context to fit within token limits.
    Prioritizes recent and important information.
    """

    def __init__(self, token_counter: TokenCounter):
        self.token_counter = token_counter
        self.logger = logging.getLogger("rich")

    def truncate_conversation_history(
        self,
        conversation: list[dict],
        max_tokens: int,
        model: str = "gpt-5",
        keep_first: int = 1,
        keep_last: int = 3,
    ) -> list[dict]:
        """
        Truncate conversation history to fit within token limit.
        Keeps first N messages (context) and last M messages (recent).
        """
        if not conversation:
            return conversation

        # Always keep system message if present
        system_messages = [msg for msg in conversation if msg.get("role") == "system"]
        other_messages = [msg for msg in conversation if msg.get("role") != "system"]

        # Calculate token usage
        current_tokens = self.token_counter.count_messages_tokens(conversation, model)

        if current_tokens <= max_tokens:
            return conversation

        self.logger.warning(
            f"Truncating conversation history from {len(conversation)} messages "
            f"({current_tokens} tokens) to fit {max_tokens} tokens"
        )

        # Keep first and last messages
        messages_to_keep = []

        if len(other_messages) <= (keep_first + keep_last):
            messages_to_keep = other_messages
        else:
            messages_to_keep = other_messages[:keep_first] + other_messages[-keep_last:]

        # Add back system messages
        result = system_messages + messages_to_keep

        # Check if still too large
        result_tokens = self.token_counter.count_messages_tokens(result, model)

        if result_tokens > max_tokens:
            # Further truncation needed - keep only system and last message
            result = system_messages + other_messages[-1:]
            self.logger.warning(
                "Aggressive truncation applied - keeping only system and last user message"
            )

        return result

    def truncate_dict(
        self, data: dict[str, Any], max_tokens: int, model: str = "gpt-5"
    ) -> dict[str, Any]:
        """
        Truncate a dictionary's values to fit within token limit.
        Removes entries starting from longest until under limit.
        """
        import json

        current_str = json.dumps(data, default=str)
        current_tokens = self.token_counter.count_tokens(current_str, model)

        if current_tokens <= max_tokens:
            return data

        self.logger.warning(
            f"Truncating dictionary from {current_tokens} tokens to fit {max_tokens} tokens"
        )

        # Sort keys by value length (descending)
        sorted_keys = sorted(data.keys(), key=lambda k: len(str(data[k])), reverse=True)

        result = data.copy()

        # Remove entries until under limit
        for key in sorted_keys:
            if current_tokens <= max_tokens:
                break

            removed_value = result.pop(key)
            removed_tokens = self.token_counter.count_tokens(str(removed_value), model)
            current_tokens -= removed_tokens
            self.logger.debug(f"Removed key '{key}' ({removed_tokens} tokens)")

        return result

    def truncate_list(
        self, data: list[Any], max_tokens: int, model: str = "gpt-5"
    ) -> list[Any]:
        """
        Truncate a list to fit within token limit.
        Keeps most recent items.
        """
        import json

        if not data:
            return data

        current_str = json.dumps(data, default=str)
        current_tokens = self.token_counter.count_tokens(current_str, model)

        if current_tokens <= max_tokens:
            return data

        self.logger.warning(
            f"Truncating list from {len(data)} items ({current_tokens} tokens) "
            f"to fit {max_tokens} tokens"
        )

        # Keep most recent items (from the end)
        result = []
        current_tokens = 0

        for item in reversed(data):
            item_str = json.dumps(item, default=str)
            item_tokens = self.token_counter.count_tokens(item_str, model)

            if current_tokens + item_tokens > max_tokens:
                break

            result.insert(0, item)
            current_tokens += item_tokens

        return result


# Global instances
_token_counter = TokenCounter()
_rate_limiter = RateLimiter()
_context_truncator = ContextTruncator(_token_counter)


def get_token_counter() -> TokenCounter:
    """Get the global token counter instance."""
    return _token_counter


def get_rate_limiter() -> RateLimiter:
    """Get the global rate limiter instance."""
    return _rate_limiter


def get_context_truncator() -> ContextTruncator:
    """Get the global context truncator instance."""
    return _context_truncator


def reset_rate_limiter(tokens_per_minute: int = 30000, requests_per_minute: int = 500):
    """Reset the global rate limiter with new limits."""
    global _rate_limiter
    _rate_limiter = RateLimiter(tokens_per_minute, requests_per_minute)
