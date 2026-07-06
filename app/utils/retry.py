"""
Retry utilities for external service calls.

Provides decorators for retrying transient failures with exponential backoff.
"""

import asyncio
import random
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

import structlog

logger = structlog.get_logger(__name__)

T = TypeVar("T")


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    exponential_base: float = 2.0,
    retryable_exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Any:
    """
    Decorator for retrying async functions with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds for first retry
        max_delay: Maximum delay in seconds between retries
        exponential_base: Base for exponential backoff calculation
        retryable_exceptions: Tuple of exception types to retry on
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        if asyncio.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                last_exception: Exception | None = None
                for attempt in range(max_retries + 1):
                    try:
                        return await func(*args, **kwargs)
                    except retryable_exceptions as exc:
                        last_exception = exc
                        if attempt == max_retries:
                            logger.error(
                                "retry_exhausted",
                                function=func.__name__,
                                attempts=attempt + 1,
                                error=type(exc).__name__,
                            )
                            raise

                        # Calculate delay with jitter
                        delay = min(
                            base_delay * (exponential_base**attempt),
                            max_delay,
                        )
                        jitter = random.uniform(0, delay * 0.1)
                        total_delay = delay + jitter

                        logger.warning(
                            "retry_attempt",
                            function=func.__name__,
                            attempt=attempt + 1,
                            max_retries=max_retries,
                            delay=total_delay,
                            error=type(exc).__name__,
                        )
                        await asyncio.sleep(total_delay)

                # This should never be reached, but just in case
                raise last_exception

            return async_wrapper
        else:

            @wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                last_exception: Exception | None = None
                for attempt in range(max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except retryable_exceptions as exc:
                        last_exception = exc
                        if attempt == max_retries:
                            logger.error(
                                "retry_exhausted",
                                function=func.__name__,
                                attempts=attempt + 1,
                                error=type(exc).__name__,
                            )
                            raise

                        # Calculate delay with jitter
                        delay = min(
                            base_delay * (exponential_base**attempt),
                            max_delay,
                        )
                        jitter = random.uniform(0, delay * 0.1)
                        total_delay = delay + jitter

                        logger.warning(
                            "retry_attempt",
                            function=func.__name__,
                            attempt=attempt + 1,
                            max_retries=max_retries,
                            delay=total_delay,
                            error=type(exc).__name__,
                        )
                        import time

                        time.sleep(total_delay)

                # This should never be reached, but just in case
                raise last_exception

            return sync_wrapper

    return decorator


# Common retry decorator for LLM calls
llm_retry = retry_with_backoff(
    max_retries=3,
    base_delay=1.0,
    max_delay=30.0,
    exponential_base=2.0,
)
