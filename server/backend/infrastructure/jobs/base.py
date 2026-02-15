"""Base job handler class with common functionality for all job handlers.

This module provides the BaseJobHandler abstract class that defines the
interface and common functionality for all job handlers. It includes error
handling patterns, logging, and support for non-retryable errors.
"""

from abc import ABC, abstractmethod
from typing import Any, TypeVar

from fastapi import Response
from pydantic import BaseModel
from structlog import get_logger

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)
R = TypeVar("R", bound=BaseModel)


class JobResult(BaseModel):
    """Standard result type for job execution.

    Attributes:
        job_id: The unique job identifier
        status: Job status (success, error, failed)
        message: Human-readable message
        data: Optional result data
        error: Optional error message if status is error/failed

    """

    job_id: str
    status: str
    message: str | None = None
    data: dict[str, Any] | None = None
    error: str | None = None


class BaseJobHandler[T: BaseModel, R: BaseModel](ABC):
    """Base class for all job handlers.

    Provides common functionality for job execution including:
    - Error handling with retryable vs non-retryable classification
    - Structured logging
    - Response creation

    Subclasses must implement the execute() method which contains
    the actual job logic.

    Type Parameters:
        T: The request type (Pydantic model)
        R: The response type (Pydantic model)
    """

    NON_RETRYABLE_PATTERNS = [
        "not found",
        "invalid",
        "malformed",
        "unauthorized",
        "forbidden",
        "already exists",
        "duplicate",
    ]

    @abstractmethod
    async def execute(self, request: T) -> R:
        """Execute the job logic.

        Args:
            request: The job request payload

        Returns:
            The job response

        Raises:
            Exception: If job execution fails (retryable by default)

        """
        pass

    def is_non_retryable_error(self, error: Exception) -> bool:
        """Check if an error should be treated as non-retryable.

        Non-retryable errors will raise a RetryException that Arq
        will not retry. Other exceptions will be retried according to
        the worker's retry configuration.

        Args:
            error: The exception to check

        Returns:
            True if the error is non-retryable, False otherwise

        """
        error_str = str(error).lower()
        return any(
            pattern in error_str for pattern in self.NON_RETRYABLE_PATTERNS
        )

    def non_retryable_error(self, detail: str) -> Response:
        """Create a 489 response to indicate non-retryable error.

        Args:
            detail: Error message describing the non-retryable condition

        Returns:
            FastAPI Response with 489 status code

        """
        return Response(
            content=detail,
            status_code=489,
            media_type="text/plain",
        )

    async def handle(self, request: T, job_id: str) -> Response | R:
        """Handle a job request with error handling.

        Wraps the execute() method with error handling logic that
        distinguishes between retryable and non-retryable errors.

        Args:
            request: The job request payload
            job_id: The job identifier for logging

        Returns:
            Either the job response or a non-retryable error response

        Raises:
            Exception: If a retryable error occurs

        """
        try:
            logger.info(
                "Job handler executing",
                job_id=job_id,
                handler=self.__class__.__name__,
            )
            result = await self.execute(request)
            logger.info(
                "Job handler completed",
                job_id=job_id,
                handler=self.__class__.__name__,
            )
            return result

        except ValueError as e:
            error_msg = str(e)
            if self.is_non_retryable_error(e):
                logger.warning(
                    "Non-retryable error in job handler",
                    job_id=job_id,
                    handler=self.__class__.__name__,
                    error=error_msg,
                )
                return self.non_retryable_error(error_msg)
            raise

        except Exception as e:
            if self.is_non_retryable_error(e):
                logger.warning(
                    "Non-retryable error in job handler",
                    job_id=job_id,
                    handler=self.__class__.__name__,
                    error=str(e),
                )
                return self.non_retryable_error(str(e))

            logger.error(
                "Retryable error in job handler",
                job_id=job_id,
                handler=self.__class__.__name__,
                error=str(e),
                exc_info=True,
            )
            raise
