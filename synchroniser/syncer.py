import os
import shutil
from pathlib import Path
import hashlib
import time
import argparse
from sync_logger import setup_logger

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

    def travers_get_modification_times(self, folder: Path):
        """Traverse a folder and return a dictionary with file paths and their modification times."""
        modification_times = {}
        for file in folder.rglob("*"):
            if file.is_file():
                modification_times[file] = file.stat().st_mtime
        return modification_times

    def sync_folders(self):
        """Synchronize source folder with replica folder."""
        start_time = time.time()  # Track start time
        self.logger.info("Starting synchronization...")

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

        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        self.logger.info(f"Synchronization completed in {elapsed_time:.2f} seconds.")

# The main method to accept command-line arguments
def main():
    parser = argparse.ArgumentParser(description="Folder Synchronizer")
    parser.add_argument("src_dir", type=str, help="Path to the source directory")
    parser.add_argument("replica_dir", type=str, help="Path to the replica directory")
    parser.add_argument("log_file", type=str, help="Path to the log file")
    parser.add_argument("interval", type=int, help="Synchronization interval in seconds")

    args = parser.parse_args()

    # Initialize Syncer with the source, replica, and log file
    syncer = Syncer(args.src_dir, args.replica_dir, args.log_file)

    # Run synchronization periodically based on the specified interval
    while True:
        syncer.sync_folders()
        time.sleep(args.interval)

if __name__ == "__main__":
    main()
