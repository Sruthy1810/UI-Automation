import logging
from pathlib import Path
from datetime import datetime

from config.config_reader import get_log_folder 

# Get log folder from external config
log_folder = Path(get_log_folder())
# Create execution folder inside logs
execution_folder = log_folder / "execution"
execution_folder.mkdir(parents=True, exist_ok=True)


# Create unique log file for this execution
log_file = execution_folder / (
    f"execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
)


# Create logger
logger = logging.getLogger("FlipkartAutomation")
logger.setLevel(logging.INFO)


# Prevent duplicate handlers
if not logger.handlers:

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Write logs to TXT file
    file_handler = logging.FileHandler(
        log_file,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    # Also show logs in terminal
    #console_handler = logging.StreamHandler()
    #console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    #logger.addHandler(console_handler)


def get_log_file():
    return str(log_file)