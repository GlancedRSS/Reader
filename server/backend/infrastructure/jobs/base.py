"""Base job handler class with common functionality for all job handlers."""

from abc import ABC, abstractmethod
from typing import Any, TypeVar

from fastapi import Response
from pydantic import BaseModel
from structlog import get_logger

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)
R = TypeVar("R", bound=BaseModel)


class JobResult(BaseModel):
    """Standard result type for job execution."""

    job_id: str
    status: str
    message: str | None = None
    data: dict[str, Any] | None = None
    error: str | None = None


class BaseJobHandler[T: BaseModel, R: BaseModel](ABC):
    """Base class for all job handlers."""

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
        """Execute the job logic."""
        pass

    def is_non_retryable_error(self, error: Exception) -> bool:
        """Check if an error should be treated as non-retryable."""
        error_str = str(error).lower()
        return any(
            pattern in error_str for pattern in self.NON_RETRYABLE_PATTERNS
        )

    def non_retryable_error(self, detail: str) -> Response:
        """Create a 489 response to indicate non-retryable error."""
        return Response(
            content=detail,
            status_code=489,
            media_type="text/plain",
        )

    async def handle(self, request: T, job_id: str) -> Response | R:
        """Handle a job request with error handling."""
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
