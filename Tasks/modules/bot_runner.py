from playwright.sync_api import sync_playwright

from modules.login import login


from browser.browser_manager import start_browser

from modules.navigation import open_pim

from modules.employee_processor import process_employees

from utils.logger import logger

from config.config_reader import get_orangehrm_url

def run_bot(file_path, username, password):

    print("BOT RUNNER STARTED")

    browser = None
    context = None

    with sync_playwright() as p:

        try:

            print("Getting login credentials...")


            logger.info("Browser started")

            browser, context, page = start_browser(p)

            print("Browser started")

            print("Logging into OrangeHRM...")

            url = get_orangehrm_url()

            login(
                page,
                username,
                password,
                url
            )

            logger.info("Login successful")

            print("Login successful")

            print("Opening PIM...")

            open_pim(page)

            logger.info("PIM opened")

            print("PIM opened")

            print("Processing employees...")

            result = process_employees(
                page,
                file_path
            )

            print("Employee processing completed")

            return result

        except Exception as e:

            logger.exception(
                f"Bot execution failed: {e}"
            )

            print(f"BOT ERROR: {e}")

            raise

        finally:

            try:

                if context:
                    context.close()

                if browser:
                    browser.close()

                logger.info(
                    "Browser closed successfully"
                )

                print("Browser closed")

            except Exception as e:

                logger.error(
                    f"Browser closing failed: {e}"
                )