from playwright.sync_api import sync_playwright
from modules.login import login
from utils.screenshot import take_screenshot
from browser.browser_manager import start_browser
from modules.navigation import open_pim
from utils.excel_validator import validate_employee_data
from modules.excel_reader import read_employee_data
from modules.employee_processor import process_employees
from utils.logger import logger
from utils.email_notification import send_exception_email
from config.config_reader import get_orangehrm_url

def run_bot(file_path, username, password):

    print("BOT RUNNER STARTED")

    browser = None
    context = None
    page = None

    with sync_playwright() as p:

        try:

            # ==========================================
            # STEP 1: READ EXCEL
            # ==========================================

            print("Reading employee data...")

            employees = read_employee_data(file_path)

            print(
                f"Employee records found: {len(employees)}"
            )

            # ==========================================
            # STEP 2: VALIDATE MANDATORY DATA
            # ==========================================

            print("Validating mandatory employee data...")

            validation_errors = validate_employee_data(
                employees
            )

            if validation_errors:

                print(
                    "Mandatory data validation failed."
                )

                # Create ONE exception message
                error_message = (
                    "Mandatory employee data is missing.\n\n"
                )

                for error in validation_errors:

                    error_message += (
                        f"Row {error['row']} - "
                        f"{error['employee']}\n"
                    )

                    error_message += (
                        f"Missing fields: "
                        f"{', '.join(error['missing'])}\n\n"
                    )

                logger.error(error_message)

                # Send ONE exception email
                send_exception_email(
                    error_message,
                    None
                )

                # STOP BOT
                return None

            print(
                "Mandatory data validation successful."
            )

            logger.info(
                "Mandatory data validation successful"
            )

            # ==========================================
            # STEP 3: START BROWSER
            # ==========================================


            print("Getting login credentials...")


            logger.info("Browser started")

            browser, context, page = start_browser(p)

            print("Browser started")

            # ==========================================
            # STEP 4: LOGIN
            # ==========================================           

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

            # ==========================================
            # STEP 5: OPEN PIM
            # ==========================================


            print("Opening PIM...")

            open_pim(page)

            logger.info("PIM opened")

            print("PIM opened")

            # ==========================================
            # STEP 6: PROCESS EMPLOYEES
            # ==========================================


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

            screenshot_path = None

            if page:

                # Capture screenshot
                screenshot_path = take_screenshot(
                    page,
                    "Bot_Exception"
                )

                # Send exception email with screenshot
                send_exception_email(
                    str(e),
                    screenshot_path
                )

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