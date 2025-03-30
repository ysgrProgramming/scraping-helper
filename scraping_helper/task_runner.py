from pathlib import Path

from pydantic import BaseModel, Field

from .auto_driver import AutoDriver
from .checkpoint_recorder import CheckpointRecorder
from .task import Task


class TaskRunnerConfig(BaseModel):
    checkpoint_path: Path = Field(default=Path("scraping_helper.ckpt"))


class TaskRunner(BaseModel):
    config: TaskRunnerConfig = Field(default=TaskRunnerConfig())
    checkpoint_recorder: CheckpointRecorder = Field(default=None, init=False)

    def model_post_init(self, __context: dict, /) -> None:
        self._checkpoint_recorder = CheckpointRecorder(
            checkpoint_path=self.config.checkpoint_path,
        )
        return super().model_post_init(__context)

    def run(self, task: Task, auto_driver: AutoDriver) -> None:
        Task.checkpoint_recorder = self.checkpoint_recorder
        task.run(auto_driver)
