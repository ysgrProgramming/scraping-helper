from scraping_helper import Task
from pathlib import Path
import tempfile


class MyTask(Task):
    a: int
    b: int
    save_path: Path

    def run(self):
        c = self.a + self.b
        with self.save_path.open("w", encoding="utf-8") as f:
            f.write(f"{self.a} + {self.b} = {c}")


def test_mytask_init():
    mytask = MyTask(name="mytask", a=2, b=3, save_path=Path("tmp"))
    assert mytask.name == "mytask"
    assert mytask.uid == "MyTask-mytask"
    assert mytask.a == 2
    assert mytask.b == 3
    assert mytask.save_path == Path("tmp")


def test_mytask_run():
    with tempfile.TemporaryDirectory() as tmpdir:
        save_path = Path(tmpdir) / "save.txt"
        mytask = MyTask(name="mytask", a=2, b=3, save_path=save_path)
        mytask.run()
        with save_path.open("r", encoding="utf-8") as f:
            msg = f.read()
            assert msg == "2 + 3 = 5"
