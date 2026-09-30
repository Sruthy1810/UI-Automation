import asyncio
from utils.logger import logger
from modules.bot_runner import run_bot


async def main():

    print("=" * 50)
    print("FLIPKART AUTOMATION STARTED")
    print("=" * 50)
    logger.info("Flipkart Automation Started")

    playwright = None
    browser = None

    try:

        playwright, browser, context, page = await run_bot()

        print("Automation is running...")

        # Keep browser open
        await page.wait_for_timeout(10000)

    except Exception as e:
        logger.error("Automation failed")
        print(f"Automation failed: {e}")

    finally:

        if browser:
            await browser.close()

        if playwright:
            await playwright.stop()

        print("=" * 50)
        print("FLIPKART AUTOMATION ENDED")
        print("=" * 50)
        logger.info("Flipkart Automation Completed")       


if __name__ == "__main__":
    asyncio.run(main())