from scraping_helper import Task, TaskRunner, TaskRunnerConfig
from pathlib import Path
import tempfile


class MyTask(Task):
    a: int
    b: int
    save_path: Path

    def run(self):
        c = self.a + self.b
        with self.save_path.open("a", encoding="utf-8") as f:
            f.write(f"{self.a} + {self.b} = {c}\n")


class ErrorTask(Task):
    def run(self):
        raise Exception("Error")


def test_run_one_task():
    with tempfile.TemporaryDirectory() as tmpdir:
        save_path = Path(tmpdir) / "result.txt"
        checkpoint_path = Path(tmpdir) / "test.ckpt"
        mytask = MyTask(name="mytask", a=2, b=3, save_path=save_path)
        config = TaskRunnerConfig(checkpoint_path=checkpoint_path)
        task_runner = TaskRunner(config=config)
        task_runner.run(mytask)

        with save_path.open("r", encoding="utf-8") as f:
            content = f.readline().rstrip()
            assert content == "2 + 3 = 5"

        with checkpoint_path.open("r", encoding="utf-8") as f:
            content = f.readline().rstrip()
            assert content == "MyTask-mytask"


def test_run_tasks():
    with tempfile.TemporaryDirectory() as tmpdir:
        save_path = Path(tmpdir) / "result.txt"
        checkpoint_path = Path(tmpdir) / "test.ckpt"
        mytask_list = [
            MyTask(name=f"mytask_{i}", a=i, b=i, save_path=save_path) for i in range(10)
        ]
        config = TaskRunnerConfig(checkpoint_path=checkpoint_path)
        task_runner = TaskRunner(config=config)
        task_runner.run(*mytask_list)

        with save_path.open("r", encoding="utf-8") as f:
            contents = [line.rstrip() for line in f.readlines()]
            for i, content in enumerate(contents):
                assert content == f"{i} + {i} = {i+i}"

        with checkpoint_path.open("r", encoding="utf-8") as f:
            contents = [line.rstrip() for line in f.readlines()]
            for i, content in enumerate(contents):
                assert content == f"MyTask-mytask_{i}"


class TaskGenerator(Task):
    num: int
    save_path: Path

    def run(self):
        mytask_list = [
            MyTask(name=f"mytask_{i}", a=i, b=i, save_path=self.save_path)
            for i in range(self.num)
        ]
        return mytask_list


def test_run_nested_tasks():
    with tempfile.TemporaryDirectory() as tmpdir:
        save_path = Path(tmpdir) / "result.txt"
        checkpoint_path = Path(tmpdir) / "test.ckpt"
        task = TaskGenerator(name="generator", num=5, save_path=save_path)
        config = TaskRunnerConfig(checkpoint_path=checkpoint_path)
        task_runner = TaskRunner(config=config)
        task_runner.run(task)

        with save_path.open("r", encoding="utf-8") as f:
            contents = [line.rstrip() for line in f.readlines()]
            for i, content in enumerate(contents):
                assert content == f"{i} + {i} = {i+i}"

        with checkpoint_path.open("r", encoding="utf-8") as f:
            contents = [line.rstrip() for line in f.readlines()]
            for i, content in enumerate(contents):
                assert content == f"MyTask-mytask_{i}"
