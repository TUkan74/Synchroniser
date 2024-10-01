# Synchroniser
The program synchronizes two folders, ensuring the replica folder maintains an identical copy of the source folder. It periodically syncs the folders and logs file operations to both the console and a log file. Folder paths, sync interval, and log file paths can be provided via command-line arguments.


## Downloadd

Clone the repository

```
git@github.com:TUkan74/Synchroniser.git
```


## Set up

To install dependencies for tests, run:

```
python install-deperndencies.py
```


## Usage

To start the program, simply run: 

```
python sync_folders.py /path/to/source /path/to/replica /path/to/logfile.log 30
```

This will synchronize the folders every 30 seconds and log operations to logfile.log.

## Testing

For testing the script, you can add,edit or delete tests in the script:

```
test_syncer.py
```

Then simply run:

```
pytest test_syncer.py
```
