# ABOUTME: Retry handler with exponential backoff for handling rate limits and transient errors
# ABOUTME: Provides decorators and context managers for robust API call handling

import asyncio
import functools
import time
import logging
from typing import Callable, Any, TypeVar, Optional
from litellm.exceptions import RateLimitError, APIError, Timeout, ServiceUnavailableError


T = TypeVar("T")


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_retries: int = 5,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
    ):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter


class RetryHandler:
    """
    Handles retries with exponential backoff for API calls.
    Specifically designed for handling rate limits and transient errors.
    """

    def __init__(self, config: Optional[RetryConfig] = None):
        self.config = config or RetryConfig()
        self.logger = logging.getLogger("rich")

    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for the next retry attempt.
        Uses exponential backoff with optional jitter.
        """
        # Exponential backoff
        delay = min(
            self.config.initial_delay
            * (self.config.exponential_base ** attempt),
            self.config.max_delay,
        )

        # Add jitter to prevent thundering herd
        if self.config.jitter:
            import random

            delay = delay * (0.5 + random.random())

        return delay

    def should_retry(self, exception: Exception, attempt: int) -> bool:
        """
        Determine if an exception should trigger a retry.
        """
        if attempt >= self.config.max_retries:
            return False

        # Retry on rate limit errors
        if isinstance(exception, RateLimitError):
            return True

        # Retry on service unavailable
        if isinstance(exception, ServiceUnavailableError):
            return True

        # Retry on timeout
        if isinstance(exception, Timeout):
            return True

        # Retry on specific API errors
        if isinstance(exception, APIError):
            # Check if it's a transient error
            error_msg = str(exception).lower()
            transient_errors = [
                "timeout",
                "rate limit",
                "too many requests",
                "service unavailable",
                "temporarily unavailable",
                "connection",
            ]
            return any(err in error_msg for err in transient_errors)

        return False

    async def execute_with_retry(
        self, func: Callable[..., T], *args, **kwargs
    ) -> T:
        """
        Execute a function with retry logic.
        """
        last_exception = None

        for attempt in range(self.config.max_retries + 1):
            try:
                # Execute the function
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)

                # Success - return result
                if attempt > 0:
                    self.logger.info(
                        f"Successfully executed after {attempt} retries"
                    )
                return result

            except Exception as e:
                last_exception = e

                # Check if we should retry
                if not self.should_retry(e, attempt):
                    self.logger.error(
                        f"Non-retryable error or max retries reached: {e}"
                    )
                    raise

                # Calculate delay
                delay = self.calculate_delay(attempt)

                # Log the retry
                self.logger.warning(
                    f"Attempt {attempt + 1}/{self.config.max_retries} failed: {e}. "
                    f"Retrying in {delay:.2f} seconds..."
                )

                # Wait before retrying
                await asyncio.sleep(delay)

        # If we get here, all retries failed
        self.logger.error(
            f"All {self.config.max_retries} retry attempts failed"
        )
        raise last_exception


def with_retry(config: Optional[RetryConfig] = None):
    """
    Decorator for adding retry logic to async functions.

    Usage:
        @with_retry()
        async def my_api_call():
            # ... API call code
            pass
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            handler = RetryHandler(config)
            return await handler.execute_with_retry(func, *args, **kwargs)

        return wrapper

    return decorator


class CircuitBreaker:
    """
    Circuit breaker pattern to prevent cascading failures.
    Opens circuit after consecutive failures, preventing further calls.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: type = Exception,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "closed"  # closed, open, half-open

        self.logger = logging.getLogger("rich")

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.state != "open":
            return False

        if self.last_failure_time is None:
            return False

        return (time.time() - self.last_failure_time) >= self.recovery_timeout

    def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """
        Execute function with circuit breaker protection.
        """
        # Check if we should attempt to reset
        if self._should_attempt_reset():
            self.logger.info("Circuit breaker: Attempting to reset (half-open)")
            self.state = "half-open"
            self.failure_count = 0

        # If circuit is open, fail fast
        if self.state == "open":
            raise Exception(
                f"Circuit breaker is OPEN. Too many consecutive failures. "
                f"Will attempt reset after {self.recovery_timeout}s."
            )

        try:
            # Execute the function
            result = func(*args, **kwargs)

            # Success - reset failure count
            if self.state == "half-open":
                self.logger.info("Circuit breaker: Reset successful (closed)")
                self.state = "closed"

            self.failure_count = 0
            return result

        except self.expected_exception as e:
            # Increment failure count
            self.failure_count += 1
            self.last_failure_time = time.time()

            # Check if we should open the circuit
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
                self.logger.error(
                    f"Circuit breaker: OPENED after {self.failure_count} consecutive failures"
                )

            raise e

    async def acall(self, func: Callable[..., T], *args, **kwargs) -> T:
        """
        Execute async function with circuit breaker protection.
        """
        # Check if we should attempt to reset
        if self._should_attempt_reset():
            self.logger.info("Circuit breaker: Attempting to reset (half-open)")
            self.state = "half-open"
            self.failure_count = 0

        # If circuit is open, fail fast
        if self.state == "open":
            raise Exception(
                f"Circuit breaker is OPEN. Too many consecutive failures. "
                f"Will attempt reset after {self.recovery_timeout}s."
            )

        try:
            # Execute the function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            # Success - reset failure count
            if self.state == "half-open":
                self.logger.info("Circuit breaker: Reset successful (closed)")
                self.state = "closed"

            self.failure_count = 0
            return result

        except self.expected_exception as e:
            # Increment failure count
            self.failure_count += 1
            self.last_failure_time = time.time()

            # Check if we should open the circuit
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
                self.logger.error(
                    f"Circuit breaker: OPENED after {self.failure_count} consecutive failures"
                )

            raise e


# Global instances
_default_retry_handler = RetryHandler()
_default_circuit_breaker = CircuitBreaker()


def get_retry_handler() -> RetryHandler:
    """Get the global retry handler instance."""
    return _default_retry_handler


def get_circuit_breaker() -> CircuitBreaker:
    """Get the global circuit breaker instance."""
    return _default_circuit_breaker
