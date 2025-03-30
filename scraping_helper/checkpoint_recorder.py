from pathlib import Path

from pydantic import BaseModel, Field


class CheckpointRecorder(BaseModel):
    checkpoint_path: Path = Field(default=Path("scraping_helper.ckpt"))
    checkpoints: set[str] = Field(default=set(), init=False)

    def model_post_init(self, __context: dict, /) -> None:
        if self.checkpoint_path.is_dir():
            self.checkpoint_path = self.checkpoint_path / "scraping_helper.ckpt"
        if self.checkpoint_path.exists():
            self.load()
        else:
            self.checkpoint_path.touch()
        return super().model_post_init(__context)

    def load(self) -> None:
        with self.checkpoint_path.open("r", encoding="utf-8") as f:
            for line in f:
                uid = line.strip()
                if uid:
                    self.checkpoints.add(uid)

    def record(self, uid: str) -> None:
        if uid in self.checkpoints:
            return
        self.checkpoints.add(uid)
        with self.checkpoint_path.open("a", encoding="utf-8") as f:
            f.write(uid + "\n")

    def exists(self, uid: str) -> bool:
        return uid in self.checkpoints
