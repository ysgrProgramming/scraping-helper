import logging
from pathlib import Path

from scraping_helper.task_runner import TaskRunner, TaskRunnerConfig


def test_task_runner_init():
    """Test TaskRunner initialization."""
    config = TaskRunnerConfig(retry_count=3, start_logging_level=logging.DEBUG)
    task_runner = TaskRunner(config=config)
    assert task_runner.config.checkpoint_path == Path("scraping_helper.ckpt")
    assert task_runner.config.retry_count == 3
    assert task_runner.config.start_logging_level == logging.DEBUG
    assert task_runner.config.done_logging_level == logging.INFO
    assert task_runner.config.skip_logging_level == logging.DEBUG
    assert task_runner.config.error_logging_level == logging.ERROR
