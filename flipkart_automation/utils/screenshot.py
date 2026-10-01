from pathlib import Path
from datetime import datetime
from utils.logger import logger


async def take_failure_screenshot(page, name):

    try:
        screenshot_dir = Path("Screenshots") / "failed"
        screenshot_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        # Remove characters that are invalid in Windows filenames
        safe_name = "".join(
            c for c in str(name)
            if c.isalnum() or c in (" ", "_", "-")
        ).strip()

        screenshot_path = (
            screenshot_dir
            / f"{safe_name}_{timestamp}.png"
        )

        await page.screenshot(
            path=str(screenshot_path),
            full_page=True,
            timeout=15000
        )

        logger.info(
            f"Failure screenshot saved: {screenshot_path}"
        )

        return str(screenshot_path)

    except Exception as e:

        logger.error(
            f"Failed to capture screenshot: {e}"
        )

        return None