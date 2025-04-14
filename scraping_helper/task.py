from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from logging import getLogger

logger = getLogger(__name__)


class TaskConfig(BaseModel):
    retry_count: int | None = Field(default=None, ge=-1)
    ignore_error: bool | None = Field(default=None)

    start_logging_level: int | None = Field(default=logging.INFO)
    done_logging_level: int | None = Field(default=logging.INFO)
    skip_logging_level: int | None = Field(default=logging.DEBUG)
    error_logging_level: int | None = Field(default=logging.ERROR)


class Task(BaseModel, ABC):
    name: str
    config: TaskConfig = Field(default_factory=TaskConfig)

    @property
    def uid(self) -> str:
        return f"{self.__class__.__name__}-{self.name}"

    @abstractmethod
    def run(self) -> list[Task] | None:
        pass
