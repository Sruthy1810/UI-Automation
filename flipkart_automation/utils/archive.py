import shutil
from pathlib import Path

from config.config_reader import get_log_folder
from utils.logger import logger
from utils.screenshot import SCREENSHOT_FAILED_DIR



def archive_old_files(keep_logs=2, keep_screenshots=2):
    """
    Keep the newest files in the logs and failed-screenshot folders.
    Move all older files into an 'archive' folder.
    """

    log_folder = Path(get_log_folder())

    folders = [
        # (source folder, archive folder, number to keep)
        (
            log_folder / "execution",
            log_folder / "archive" / "execution",
            keep_logs
        ),
        (
            SCREENSHOT_FAILED_DIR,
            SCREENSHOT_FAILED_DIR.parent / "archive" / "failed",
            keep_screenshots
        ),
    ]

    for source, archive, keep in folders:

        try:
            if not source.exists():
                continue

            files = sorted(
                (f for f in source.iterdir() if f.is_file()),
                key=lambda f: f.stat().st_mtime,
                reverse=True
            )

            old_files = files[keep:]

            if not old_files:
                continue

            archive.mkdir(parents=True, exist_ok=True)

            for file in old_files:

                try:
                    destination = archive / file.name

                    if destination.exists():
                        destination = archive / (
                            f"{file.stem}_{int(file.stat().st_mtime)}{file.suffix}"
                        )

                    shutil.move(str(file), str(destination))

                    logger.info(f"Archived: {file.name}")

                except Exception as e:
                    logger.error(f"Could not archive {file.name}: {e}")

        except Exception as e:
            logger.error(f"Archive failed for {source}: {e}")