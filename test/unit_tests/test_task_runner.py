import logging
from pathlib import Path
import tempfile
from scraping_helper.task_runner import TaskRunner, TaskRunnerConfig


def test_task_runner_config_init():
    config = TaskRunnerConfig(checkpoint_path=Path("path"), retry_count=3, start_logging_level=logging.DEBUG)
    assert config.checkpoint_path == Path("path")
    assert config.retry_count == 3
    assert config.start_logging_level == logging.DEBUG

def test_task_runner_init():
    """Test TaskRunner initialization."""
    config = TaskRunnerConfig(retry_count=3, start_logging_level=logging.DEBUG)
    task_runner = TaskRunner(config=config)
    assert task_runner.config == TaskRunnerConfig(retry_count=3, start_logging_level=logging.DEBUG)

def test_task_runner_empty_run():
    with tempfile.TemporaryDirectory() as temp_dir:
        checkpoint_path = Path(temp_dir) / "test.ckpt"
        config = TaskRunnerConfig(checkpoint_path=checkpoint_path)
        task_runner = TaskRunner(config=config)
        task_runner.run()
        assert checkpoint_path.exists()