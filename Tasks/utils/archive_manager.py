import os
import shutil


def archive_old_files(folder_path, archive_path, keep_count=5):
    """
    Keep the latest `keep_count` files in the source folder.
    Move older files to the archive folder.
    """

    if not os.path.exists(folder_path):
        return

    os.makedirs(archive_path, exist_ok=True)

    files = []

    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)

        if os.path.isfile(file_path):
            files.append(file_path)

    # Sort by modified time - newest first
    files.sort(
        key=lambda file: os.path.getmtime(file),
        reverse=True
    )

    # Files after the latest 5
    old_files = files[keep_count:]

    for file_path in old_files:

        file_name = os.path.basename(file_path)
        destination = os.path.join(archive_path, file_name)

        shutil.move(file_path, destination)

        print(f"Archived: {file_name}")


def archive_execution_files(base_path):

    logs_folder = os.path.join(
        base_path,
        "logs",
        "executions"
    )

    screenshots_folder = os.path.join(
        base_path,
        "Screenshots",
        "failed"
    )

    logs_archive = os.path.join(
        base_path,
        "Archive",
        "Logs"
    )

    screenshots_archive = os.path.join(
        base_path,
        "Archive",
        "Screenshots"
    )

    # Archive logs
    archive_old_files(
        logs_folder,
        logs_archive,
        keep_count=5
    )

    # Archive failed screenshots
    archive_old_files(
        screenshots_folder,
        screenshots_archive,
        keep_count=5
    )