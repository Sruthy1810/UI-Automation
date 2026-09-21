from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
SCREENSHOT_DIR = BASE_DIR / "Screenshots" / "failed"

SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def take_screenshot(page, employee_name):

    safe_name = employee_name.replace(" ", "_")

    screenshot_path = SCREENSHOT_DIR / f"{safe_name}.png"

    page.screenshot(
        path=str(screenshot_path),
        full_page=True
    )

    return screenshot_path