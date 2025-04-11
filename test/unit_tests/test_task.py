from dataclasses import dataclass
from scraping_helper import Task
from pathlib import Path

@dataclass
class MyTask(Task):
    a: int
    b: int
    save_path: Path

    def run(self):
        c = self.a + self.b


def test_mytask_init():
    mytask = MyTask(name="mytask", a=2, b=3, save_path=Path("tmp"))
    assert mytask.name == "mytask"
    assert mytask.uid == "MyTask-mytask"
    assert mytask.a == 2
    assert mytask.b == 3
    assert mytask.save_path == Path("tmp")
