from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar

from pydantic import BaseModel, Field

from .auto_driver import AutoDriver
from .checkpoint_recorder import CheckpointRecorder
from .slack_notificater import SlackNotificater


class Task(BaseModel, ABC):
    name: str = Field(..., description="タスク名")
    start_notificater: SlackNotificater | None = Field(default=None)
    done_noteificater: SlackNotificater | None = Field(default=None)
    error_notificater: SlackNotificater | None = Field(default=None)
    checkpoint_recorder: ClassVar[CheckpointRecorder] = Field(default=None)

    @property
    def uid(self) -> str:
        return f"{self.__class__.__name__}-{self.name}"

    def run(self) -> bool:
        if self.__class__.checkpoint_recorder.exists(self.uid):
            print(f"{self.uid} は既に記録済みです。")
            return True
        if self.start_notificater:
            self.start_notificater.notify(f"{self.uid} の処理を開始します。")
        try:
            self.execute()
        except Exception as e:  # noqa: BLE001
            if self.error_notificater:
                self.error_notificater.notify(f"{self.uid}でエラー発生: {e}")
            return False
        self.done()
        return True

    def done(self) -> None:
        """タスク完了時にチェックポイントに登録(ファイルに 1 行追記)"""
        self.__class__.checkpoint_recorder.record(self.uid)
        self.done_noteificater.notify(f"{self.uid}の処理が完了しました。")

    @abstractmethod
    def execute(self, auto_driver: AutoDriver) -> None:
        pass
