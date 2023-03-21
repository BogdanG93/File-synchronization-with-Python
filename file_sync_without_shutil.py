import os
import argparse
import hashlib
import time
from datetime import datetime


def hash_file(filename):
    hasher = hashlib.md5()
    with open(filename, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()


def sync_folders(source_folder, replica_folder, log_file):
    if not os.path.exists(source_folder):
        raise Exception("ERROR! The source folder does not exist.")
    if not os.path.exists(replica_folder):
        os.makedirs(replica_folder)

    for root, dirs, files in os.walk(source_folder):
        for file in files:
            source_file = os.path.join(root, file)
            replica_file = os.path.join(replica_folder, os.path.relpath(source_file, source_folder))
            if not os.path.exists(replica_file) or hash_file(source_file) != hash_file(replica_file):
                with open(source_file, 'rb') as f1, open(replica_file, 'wb') as f2:
                    f2.write(f1.read())
                current_time = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
                log_file.write(f"{current_time}: Copied {source_file} to {replica_file}\n")
                print(f"{current_time}: Copied {source_file} to {replica_file}")

        for file in os.listdir(replica_folder):
            replica_file = os.path.join(replica_folder, file)
            source_file = os.path.join(source_folder, os.path.relpath(replica_file, replica_folder))
            if not os.path.exists(source_file):
                os.remove(replica_file)
                current_time = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
                log_file.write(f"{current_time}: Removed {replica_file}\n")
                print(f"{current_time}: Removed {replica_file}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Synchronize two folders.')
    parser.add_argument('source_folder', help='path to the source folder')
    parser.add_argument('replica_folder', help='path to the replica folder')
    parser.add_argument('sync_interval', type=int, help='interval for synchronization in seconds')
    parser.add_argument('log_file_path', help='path to the log file')
    args = parser.parse_args()

    current_time = datetime.now().strftime('%d-%m-%Y %H:%M:%S')

    print(f"Folder synchronization script running...\n"
          f"Date and time: {current_time}\n"
          f"Source folder: {args.source_folder}\n"
          f"Replica folder: {args.replica_folder}\n"
          f"Synchronization interval: {args.sync_interval} seconds\n"
          f"Log file path: {args.log_file_path}\n")

    log_file = open(args.log_file_path, 'a')
    log_file.write('\nNew session running...\n')

    try:
        while True:
            sync_folders(args.source_folder, args.replica_folder, log_file)
            time.sleep(args.sync_interval)
    except KeyboardInterrupt:
        pass

    log_file.close()
