import os
import shutil
from pathlib import Path
from typing import Dict
import hashlib
from logger import setup_logger

class Syncer:
    def __init__(self, source: str, replica: str, log_file: str = None):
        self.source = Path(source)
        self.replica = Path(replica)
        self.logger = setup_logger(log_file)



    def calculate_md5(self, file_path: Path) -> str:
        """Calculate MD5 checksum of a file."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def travers_get_modification_times(self, folder: Path) -> Dict[Path, float]:
        """Traverse a folder and return a dictionary with file paths and their modification times."""
        modification_times = {}
        for file in folder.rglob("*"):
            if file.is_file():
                modification_times[file] = file.stat().st_mtime
        return modification_times

    def sync_folders(self):
        """Synchronize source folder with replica folder."""
        # Sync files from source to replica
        for src_file in self.source.rglob("*"):
            replica_file = self.replica / src_file.relative_to(self.source)
            if src_file.is_file():
                # If the file doesn't exist in the replica or is different, copy it over
                if not replica_file.exists() or self.calculate_md5(src_file) != self.calculate_md5(replica_file):
                    if not replica_file.parent.exists():
                        replica_file.parent.mkdir(parents=True)
                        self.logger.info(f"Created directory: {replica_file.parent}")
                    shutil.copy2(src_file, replica_file)
                    self.logger.info(f"Copied file: {src_file} to {replica_file}")

        # Remove files and directories in replica that are not in source
        for replica_file in self.replica.rglob("*"):
            src_file = self.source / replica_file.relative_to(self.replica)
            if not src_file.exists():
                if replica_file.is_file():
                    replica_file.unlink()
                    self.logger.info(f"Deleted file: {replica_file}")
                else:
                    shutil.rmtree(replica_file)
                    self.logger.info(f"Deleted directory: {replica_file}")

