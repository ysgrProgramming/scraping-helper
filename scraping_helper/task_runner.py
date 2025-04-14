import logging
from collections import deque
from logging import getLogger
from pathlib import Path
from pydantic import Field, BaseModel
from .checkpoint_recorder import CheckpointRecorder
from .task import Task

logger = getLogger(__name__)


class TaskRunnerConfig(BaseModel):
    checkpoint_path: Path = Field(default=Path("scraping_helper.ckpt"))
    retry_count: int = Field(default=0, ge=-1)
    ignore_error: bool = Field(default=False)

    start_logging_level: int = Field(default=logging.INFO)
    done_logging_level: int = Field(default=logging.INFO)
    skip_logging_level: int = Field(default=logging.DEBUG)
    error_logging_level: int = Field(default=logging.ERROR)


class TaskNode(BaseModel):
    task: Task
    children: list["TaskNode"] | None = Field(default=None)
    parent: "TaskNode" | None = Field(default=None)
    children_cursor: int = 0

    def next_child(self):
        if self.children is None or len(self.children) <= self.children_cursor:
            return None
        child = self.children[self.children_cursor]
        self.children_cursor += 1
        return child


def resolve_value(preferred_value, default_value):
    if preferred_value is None:
        return default_value
    else:
        return preferred_value


class TaskRunner(BaseModel):
    """タスクを実行するクラス"""

    config: TaskRunnerConfig = Field(default_factory=TaskRunnerConfig)

    def run(self, *args: Task) -> None:
        checkpoint_recorder = CheckpointRecorder(
            checkpoint_path=self.config.checkpoint_path,
        )
        nodes = deque(TaskNode(task=task) for task in args)
        while nodes:
            node = nodes.popleft()
            task = node.task
            if checkpoint_recorder.exists(task.uid):
                skip_logging_level = resolve_value(
                    task.config.skip_logging_level, self.config.skip_logging_level
                )
                logger.log(
                    skip_logging_level,
                    "%s は既に記録済みです。",
                    task.uid,
                )
                if node.parent is not None:
                    brother = node.next_child()
                    if brother is not None:
                        nodes.appendleft(brother)
                continue
            try:
                start_logging_level = resolve_value(
                    task.config.start_logging_level, self.config.start_logging_level
                )
                logger.log(start_logging_level, "%s を開始します", task.uid)
                children = task.run()

                if node.parent is not None:
                    brother = node.parent.next_child()
                    if brother is not None:
                        nodes.appendleft(brother)
                if children:
                    children_nodes = [
                        TaskNode(task=task, parent=node) for task in children
                    ]
                    node.children = children_nodes
                    nodes.appendleft(node.next_child())
                checkpoint_recorder.record(task.uid)
                done_logging_level = resolve_value(
                    task.config.done_logging_level, self.config.done_logging_level
                )
                logger.log(
                    done_logging_level,
                    "%s が完了しました",
                    task.uid,
                )
            except Exception as e:  # noqa: BLE001
                error_logging_level = resolve_value(
                    task.config.error_logging_level, self.config.error_logging_level
                )
                logger.log(
                    error_logging_level,
                    "%sでエラー発生: %s",
                    task.uid,
                    e,
                )
