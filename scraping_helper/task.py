from pydantic import BaseModel
from abc import ABC, abstractmethod
from typing import ClassVar
from pathlib import Path


class Task(BaseModel, ABC):
    name: str
    checkpoints_file_path: ClassVar[Path] = Path("checkpoints.txt")
    checkpoints: ClassVar[set[str]] = set()

    @property
    def uid(self) -> str:
        return f"{self.__class__.__name__}-{self.name}"

    @classmethod
    def load_checkpoints(cls) -> None:
        if cls.checkpoints_file_path.exists():
            with cls.checkpoints_file_path.open("r", encoding="utf-8") as f:
                for line in f:
                    uid = line.strip()
                    if uid:
                        cls.checkpoints.add(uid)
            print(
                f"チェックポイント: {len(cls.checkpoints)} 件の完了済みタスクを読み込みました。"
            )

    def run(self):
        if self.uid in self.__class__.checkpoints:
            print(f"{self.uid} は既に記録済みです。")
            return
        try:
            self.execute()
        except Exception as e:
            print(f"エラー発生: {e}")
            return
        self.done()

    def done(self):
        """タスク完了時にチェックポイントに登録（ファイルに 1 行追記）"""
        self.__class__.checkpoints.add(self.uid)
        with self.__class__.checkpoints_file_path.open("a", encoding="utf-8") as f:
            f.write(self.uid + "\n")
        print(f"タスク完了: {self.uid} をチェックポイントに記録しました。")

    @abstractmethod
    def execute(self):
        pass
