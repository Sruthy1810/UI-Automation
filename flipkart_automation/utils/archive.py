import shutil
from pathlib import Path

from config.config_reader import get_log_folder
from utils.logger import logger


def archive_old_files(keep=2):
    """
    Keep the newest `keep` files in the logs and failed-screenshot folders.
    Move all older files into an 'archive' folder next to them.
    """

    log_folder = Path(get_log_folder())

    folders = [
        # (source folder, archive folder)
        (
            log_folder / "execution",
            log_folder / "archive" / "execution"
        ),
        (
            Path("Screenshots") / "failed",
            Path("Screenshots") / "archive" / "failed"
        ),
    ]

    for source, archive in folders:

        try:
            if not source.exists():
                continue

            # Only files, newest first
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

                    # Avoid overwriting if the same name already exists
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