from datetime import datetime
from pathlib import Path
from utils.logger import logger
from config.config_reader import get_screenshot_folder


def take_screenshot(page, employee_name,error_type=None):

    try:
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

        if error_type:

            safe_error = (
                error_type
                .replace(" ", "_")
                .replace("/", "_")
            )

            file_name = (
                f"{safe_name}_{safe_error}_{timestamp}.png"
            )

        else:

            file_name = (
                f"{safe_name}_{timestamp}.png"
            )


        screenshot_path = (
            Path(screenshot_folder)
            / f"{safe_name}_{timestamp}.png"
        )

        page.screenshot(
            path=str(screenshot_path),
            full_page=True
        )

        logger.info(
            f"Screenshot saved: {screenshot_path}"
        )

        return str(screenshot_path)


    except Exception as e:

        logger.error(
            f"Unable to capture screenshot: {e}"
        )

        return None

