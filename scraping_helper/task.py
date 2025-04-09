from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from logging import getLogger

logger = getLogger(__name__)


@dataclass
class TaskConfig:
    retry_count: int | None = field(default=-1, description="リトライ回数")

    start_logging_level: int | None = field(default=logging.INFO)
    done_logging_level: int | None = field(default=logging.INFO)
    skip_logging_level: int | None = field(default=logging.DEBUG)
    error_logging_level: int | None = field(default=logging.ERROR)


@dataclass
class Task(ABC):
    name: str = field(..., description="タスク名")
    config: TaskConfig = field(default=TaskConfig(), description="タスクの設定")

    @property
    def uid(self) -> str:
        return f"{self.__class__.__name__}-{self.name}"

    @abstractmethod
    def run(self) -> None:
        pass
