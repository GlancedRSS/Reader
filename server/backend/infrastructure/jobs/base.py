from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel
from structlog import get_logger

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)
R = TypeVar("R", bound=BaseModel)


class BaseJobHandler[T: BaseModel, R: BaseModel](ABC):
    @abstractmethod
    async def execute(self, request: T) -> R:
        pass

    async def handle(self, request: T, job_id: str) -> R:
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
