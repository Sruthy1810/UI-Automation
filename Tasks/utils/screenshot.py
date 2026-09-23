from datetime import datetime
from pathlib import Path

from config.config_reader import get_screenshot_folder


def take_screenshot(page, employee_name):

    screenshot_folder = get_screenshot_folder()

    Path(
        screenshot_folder
    ).mkdir(
        parents=True,
        exist_ok=True
    )

    safe_name = (
        employee_name
        .replace(" ", "_")
        .replace("/", "_")
    )

    timestamp = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    screenshot_path = (
        Path(screenshot_folder)
        / f"{safe_name}_{timestamp}.png"
    )

    page.screenshot(
        path=str(screenshot_path),
        full_page=True
    )

    return str(screenshot_path)