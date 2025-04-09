import logging
from collections import deque
from dataclasses import dataclass, field
from logging import getLogger
from pathlib import Path

from .checkpoint_recorder import CheckpointRecorder
from .task import Task

logger = getLogger(__name__)


@dataclass
class TaskRunnerConfig:
    checkpoint_path: Path = field(default=Path("scraping_helper.ckpt"))
    retry_count: int = field(default=-1, description="リトライ回数")

    start_logging_level: int = field(default=logging.INFO)
    done_logging_level: int = field(default=logging.INFO)
    skip_logging_level: int = field(default=logging.DEBUG)
    error_logging_level: int = field(default=logging.ERROR)


@dataclass
class TaskRunner:
    """タスクを実行するクラス"""

    config: TaskRunnerConfig = field(default=TaskRunnerConfig())

    def run(self, *args: Task) -> None:
        checkpoint_recorder = CheckpointRecorder(
            checkpoint_path=self.config.checkpoint_path,
        )
        tasks = deque(args)
        while tasks:
            task = tasks.popleft()
            if checkpoint_recorder.exists(task.uid):
                logger.log(
                    self.config.skip_logging_level,
                    "%s は既に記録済みです。",
                    task.uid,
                )
                continue
            try:
                logger.log(self.config.start_logging_level, "%s を開始します", task.uid)
                children = task.run()
                if children:
                    tasks.extendleft(children)
                checkpoint_recorder.record(task.uid)
                logger.log(
                    self.config.start_logging_level,
                    "%s が完了しました",
                    task.uid,
                )
            except Exception as e:  # noqa: BLE001
                logger.log(
                    self.config.error_logging_level,
                    "%sでエラー発生: %s",
                    task.uid,
                    e,
                )
