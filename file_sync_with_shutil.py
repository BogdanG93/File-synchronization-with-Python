import os  # for operating system functions
import shutil  # for high-level file operations
import argparse  # for command line argument parsing
import hashlib  # for generating MD5 hash of files
import time  # for pausing the script between synchronization intervals
from datetime import datetime  # for logging date and time


def hash_file(filename):
    """Return the MD5 hash of a file."""
    hasher = hashlib.md5()
    with open(filename, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()


def sync_folders(source_folder, replica_folder, log_file):
    """Synchronize two folders."""
    # Ensure that both folders exist
    if not os.path.exists(source_folder):
        raise Exception("ERROR! The source folder does not exist.")
    if not os.path.exists(replica_folder):
        os.makedirs(replica_folder)

    # Iterate through the source folder
    for root, dirs, files in os.walk(source_folder):
        # Copy each file to the replica folder if it is not already there or if it has been modified
        for file in files:
            source_file = os.path.join(root, file)
            replica_file = os.path.join(replica_folder, os.path.relpath(source_file, source_folder))
            # If the replica file does not exist or the source and replica files have different MD5 hashes,
            # copy the source file to the replica folder
            if not os.path.exists(replica_file) or hash_file(source_file) != hash_file(replica_file):
                shutil.copy2(source_file, replica_file)
                # Log the file copy operation to the log file and console output
                current_time = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
                log_file.write(f"{current_time}: Copied {source_file} to {replica_file}\n")
                print(f"{current_time}: Copied {source_file} to {replica_file}")

        # Remove any files in the replica folder that are not in the source folder
        for file in os.listdir(replica_folder):
            replica_file = os.path.join(replica_folder, file)
            source_file = os.path.join(source_folder, os.path.relpath(replica_file, replica_folder))
            # If the source file does not exist, remove the replica file from the replica folder
            if not os.path.exists(source_file):
                os.remove(replica_file)
                # Log the file removal operation to the log file and console output
                current_time = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
                log_file.write(f"{current_time}: Removed {replica_file}\n")
                print(f"{current_time}: Removed {replica_file}")


if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Synchronize two folders.')
    parser.add_argument('source_folder', help='path to the source folder')
    parser.add_argument('replica_folder', help='path to the replica folder')
    parser.add_argument('sync_interval', type=int, help='interval for synchronization in seconds')
    parser.add_argument('log_file_path', help='path to the log file')
    args = parser.parse_args()

    current_time = datetime.now().strftime('%d-%m-%Y %H:%M:%S')

    # Print information about the script and command line arguments
    print(f"Folder synchronization script running...\n"
          f"Date and time: {current_time}\n"
          f"Source folder: {args.source_folder}\n"
          f"Replica folder: {args.replica_folder}\n"
          f"Synchronization interval: {args.sync_interval} seconds\n"
          f"Log file path: {args.log_file_path}\n")

    # Open the log file in append mode
    log_file = open(args.log_file_path, 'a')
    # Add blank line for delimitation of sessions in the log file
    log_file.write('\nNew session running...\n')

    try:
        while True:
            # Synchronize the two folders
            sync_folders(args.source_folder, args.replica_folder, log_file)
            # Pause the script for the specified synchronization interval
            time.sleep(args.sync_interval)
    except KeyboardInterrupt:
        pass

    # Close the log file
    log_file.close()
