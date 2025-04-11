import tempfile
from pathlib import Path
from scraping_helper.checkpoint_recorder import CheckpointRecorder

def test_init_directory():
    with tempfile.TemporaryDirectory() as tmp_dir:
        directory = Path(tmp_dir) / "test_directory"
        directory.mkdir()
        checkpoint_recorder = CheckpointRecorder(checkpoint_path=directory)
        expected_file = directory / "scraping_helper.ckpt"
        assert checkpoint_recorder.checkpoint_path == expected_file
        assert expected_file.exists()
        assert checkpoint_recorder.checkpoints == set()

def test_init_file():
    with tempfile.TemporaryDirectory() as tmp_dir:
        checkpoint_file = Path(tmp_dir) / "checkpoint_test.ckpt"
        checkpoint_file.write_text("uid1\nuid2\n")
        checkpoint_recorder = CheckpointRecorder(checkpoint_path=checkpoint_file)
        assert checkpoint_recorder.checkpoints == {"uid1", "uid2"}

def test_record():
    with tempfile.TemporaryDirectory() as tmp_dir:
        checkpoint_file = Path(tmp_dir) / "checkpoint_test.ckpt"
        checkpoint_file.write_text("uid1\n")
        checkpoint_recorder = CheckpointRecorder(checkpoint_path=checkpoint_file)
        checkpoint_recorder.record("uid2")
        assert "uid2" in checkpoint_recorder.checkpoints
        lines = checkpoint_file.read_text().splitlines()
        assert "uid2" in lines
        original_length = len(lines)
        checkpoint_recorder.record("uid2")
        assert len(checkpoint_file.read_text().splitlines()) == original_length

def test_exists():
    with tempfile.TemporaryDirectory() as tmp_dir:
        checkpoint_file = Path(tmp_dir) / "checkpoint_test.ckpt"
        checkpoint_file.write_text("uid1\n")
        checkpoint_recorder = CheckpointRecorder(checkpoint_path=checkpoint_file)
        assert checkpoint_recorder.exists("uid1")
        assert not checkpoint_recorder.exists("uid2")