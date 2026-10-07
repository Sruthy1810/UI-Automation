import asyncio
from pathlib import Path
from datetime import datetime
from PIL import ImageGrab
from utils.logger import logger

SCREENSHOT_FAILED_DIR = Path(__file__).resolve().parent.parent / "Screenshots" / "failed"

async def take_failure_screenshot(page, name):

    try:

        # Absolute path, same no matter where the bot is launched from
        
        screenshot_dir = SCREENSHOT_FAILED_DIR
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

        try:
            await page.bring_to_front()
            await asyncio.sleep(0.5)
        
        except Exception:
            pass

        def grab_screen():
            image = ImageGrab.grab(all_screens=True)
            image.save(str(screenshot_path))

        await asyncio.to_thread(grab_screen)

        logger.info(
            f"Failure screenshot saved: {screenshot_path}"
        )

        return str(screenshot_path)

    except Exception as e:

        logger.error(
            f"Failed to capture screenshot: {e}"
        )

        return None