from playwright.async_api import async_playwright
from config.config_reader import get_session_file

async def start_browser():

    playwright = await async_playwright().start()

    browser = await playwright.chromium.launch(
        headless=False,
        args=[
            "--window-size=1920,1080",
            "--window-position=0,0"
        ]
    )

    session_file = get_session_file()



    print("Session file:", session_file)
    print("Session type:", type(session_file))

    if session_file.exists():

        print("Saved session found.")
        print("Opening Flipkart using saved session...")

        context = await browser.new_context(
                storage_state=str(session_file),
                viewport = {
                    "width":1920,
                    "height":1080
                }
        )

    else:

        print("No saved session found.")
        print("Creating new browser session...")

        context = await browser.new_context(
            viewport={
            "width": 1920,
            "height": 1080
        }
        )

    page = await context.new_page()

    return playwright, browser, context, page