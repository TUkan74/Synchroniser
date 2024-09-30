import shutil
import tempfile
from pathlib import Path
from typing import Generator
import os

import pytest
from synchroniser.syncer import Syncer


@pytest.fixture
def temp_directories() -> Generator[tuple[str, str], None, None]:
    src_dir = tempfile.mkdtemp()
    replica_dir = tempfile.mkdtemp()
    yield src_dir, replica_dir
    # Set all files in src_dir and replica_dir to be writable before removing the directories
    for dir_path in [src_dir, replica_dir]:
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                # Set file permission to writable (0o666)
                os.chmod(file_path, 0o666)
    shutil.rmtree(src_dir)
    shutil.rmtree(replica_dir)



def test_sync_folders_no_files(temp_directories: tuple[str, str]) -> None:
    src_dir, replica_dir = temp_directories
    syncer = Syncer(src_dir, replica_dir)
    syncer.sync_folders()
    assert len(list(Path(replica_dir).iterdir())) == 0


def test_sync_folders_with_files(temp_directories: tuple[str, str]) -> None:
    src_dir, replica_dir = temp_directories
    syncer = Syncer(src_dir, replica_dir)
    file1 = Path(src_dir) / "file1.txt"
    file1.touch()
    file2 = Path(src_dir) / "file2.txt"
    file2.touch()
    syncer.sync_folders()
    replica_files = list(Path(replica_dir).iterdir())
    assert len(replica_files) == 2
    assert Path(replica_dir) / "file1.txt" in replica_files
    assert Path(replica_dir) / "file2.txt" in replica_files


def test_sync_folders_delete_files_in_replica(temp_directories: tuple[str, str]) -> None:
    src_dir, replica_dir = temp_directories
    syncer = Syncer(src_dir, replica_dir)

    # Create a file in source and sync
    file1 = Path(src_dir) / "file1.txt"
    file1.touch()
    syncer.sync_folders()
    
    # Ensure it exists in replica
    assert (Path(replica_dir) / "file1.txt").exists()

    # Now delete the file from the source and sync again
    file1.unlink()
    syncer.sync_folders()

    # Ensure the file is also deleted in replica
    assert not (Path(replica_dir) / "file1.txt").exists()


def test_sync_folders_update_file_in_replica(temp_directories: tuple[str, str]) -> None:
    src_dir, replica_dir = temp_directories
    syncer = Syncer(src_dir, replica_dir)

    # Create a file in source
    file1 = Path(src_dir) / "file1.txt"
    file1.write_text("Initial content")
    syncer.sync_folders()

    # Ensure it exists in replica
    replica_file1 = Path(replica_dir) / "file1.txt"
    assert replica_file1.exists()

    # Modify the file in source
    file1.write_text("Updated content")
    syncer.sync_folders()

    # Ensure the file is updated in the replica
    assert replica_file1.read_text() == "Updated content"

def test_sync_folders_with_subdirectories(temp_directories: tuple[str, str]) -> None:
    src_dir, replica_dir = temp_directories
    syncer = Syncer(src_dir, replica_dir)
    
    sub_dir = Path(src_dir) / "subdir"
    sub_dir.mkdir()
    
    file1 = sub_dir / "file1.txt"
    file1.touch()

    syncer.sync_folders()

    # Ensure that the subdirectory and file are replicated
    assert (Path(replica_dir) / "subdir").exists()
    assert (Path(replica_dir) / "subdir" / "file1.txt").exists()


def test_travers_get_modification_times(temp_directories: tuple[str, str]) -> None:
    src_dir, replica_dir = temp_directories
    syncer = Syncer(src_dir, replica_dir)
    file1 = Path(src_dir) / "file1.txt"
    file1.touch()
    file2 = Path(src_dir) / "file2.txt"
    file2.touch()
    modified_files = syncer.travers_get_modification_times(Path(src_dir))
    assert len(modified_files) == 2
    assert file1 in modified_files
    assert file2 in modified_files


def test_sync_folders_with_file_permissions(temp_directories: tuple[str, str]) -> None:
    src_dir, replica_dir = temp_directories
    syncer = Syncer(src_dir, replica_dir)

    file1 = Path(src_dir) / "file1.txt"
    file1.touch()

    # Set read-only permission on the source file
    file1.chmod(0o444)
    syncer.sync_folders()

    replica_file1 = Path(replica_dir) / "file1.txt"

    # Ensure the file exists in the replica
    assert replica_file1.exists()

    # Check that permissions are preserved
    assert oct(replica_file1.stat().st_mode & 0o777) == "0o444"


def test_sync_folders_with_logging(temp_directories: tuple[str, str]) -> None:
    src_dir, replica_dir = temp_directories
    log_file = Path(tempfile.mkdtemp()) / "sync.log"
    syncer = Syncer(src_dir, replica_dir, str(log_file))

    file1 = Path(src_dir) / "file1.txt"
    file1.touch()

    syncer.sync_folders()

    # Check that the log file is created and contains expected content
    assert log_file.exists()

    # Check that the log file contains log messages about file operations
    with open(log_file, "r") as f:
        logs = f.read()
        assert "Copied file" in logs
        assert str(file1) in logs
