from playwright.sync_api import sync_playwright
import time
import tkinter as tk
from login import get_login_credentials
from excel_reader import ( read_employee_data,update_employee_status )
from employee import create_employee
from logger import logger
from pathlib import Path
from screenshot import take_screenshot
from datetime import datetime
from email_notification import ( send_start_email,send_completion_email)



# =========================================================
# START EXECUTION TIMER
# =========================================================


start_time = datetime.now()


# =========================================================
# SEND START EMAIL
# =========================================================

send_start_email(start_time)


# =========================================================
# VARIABLES
# =========================================================

successful_records = 0
failed_records = 0

errors = []



#   PROJECT PATH   #

base_dir = Path(__file__).resolve().parent

file_path = base_dir / "EmployeeData.xlsx"



#screen size
root = tk.Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.destroy()

try:

    logger.info("Bot execution started")
    #opening chromium
    with sync_playwright() as p:


        username, password = get_login_credentials()

        logger.info("Login credentials retrieved from config file")

        browser = p.chromium.launch(
            headless=False,
            args=[
                f"--window-size={screen_width},{screen_height}",
                "--window-position=0,0"
            ]
        )

        context = browser.new_context(
            viewport={
                "width": screen_width,
                "height": screen_height
            }
        )


        page = context.new_page()
        page.goto("https://opensource-demo.orangehrmlive.com/web/index.php/auth/login")
        logger.info("OrangeHRM application opened")

        time.sleep(3)
        

        page.get_by_placeholder("Username").fill(username)

        page.get_by_placeholder("Password").fill(password)

        page.get_by_role(
            "button",
            name="Login"
        ).click()

        

        print("Login successful")
        page.get_by_text(
            "Dashboard",
            exact=True
        )

        logger.info("Login successful")

        print("Dashboard displayed")
        logger.info("Dashboard displayed successfully")
        time.sleep(5)

        page.get_by_text("PIM", exact=True).click()
        page.get_by_text(
        "PIM",
        exact=True
    )

        print("PIM page opened")
        logger.info("PIM page opened successfully")
        time.sleep(3)
        
        
        employees = read_employee_data(file_path)

        total_employees = len(employees)

        logger.info(f"Employee data read from Excel. Total employees: {len(employees)}")


        for employee in employees:

            row_number = employee["_row_number"]

            first_name = str(
                employee["First Name"]
            ).strip()

            last_name = str(
                employee["Last Name"]
            ).strip()

            employee_name = (
                    f"{first_name} {last_name}"
                )

            try:

                # ==========================================
                # OPEN ADD EMPLOYEE
                # ==========================================

                page.get_by_role(
                    "link",
                    name="Add Employee",
                    exact=True
                ).click()

                page.get_by_placeholder(
                    "First Name"
                ).wait_for(
                    state="visible"
                )

                print(
                    f"\nCreating employee: "
                    f"{first_name} {last_name}"
                )

                logger.info(
                    f"Add Employee page opened for "
                    f"{first_name} {last_name}"
                )

                # ==========================================
                # CREATE EMPLOYEE
                # ==========================================

                success = create_employee(
                    page,
                    employee
                )

                # ==========================================
                # SUCCESS
                # ==========================================

                if success:

                    update_employee_status(
                        file_path,
                        row_number,
                        "Success",
                        "Employee created and document uploaded successfully"
                    )

                    successful_records += 1

                    print(
                        f"Completed: "
                        f"{first_name} {last_name}"
                    )

                    logger.info(
                        f"Employee created successfully: "
                        f"{first_name} {last_name}"
                    )

                # ==========================================
                # FAILED
                # ==========================================

                else:

                    failed_records += 1

                    update_employee_status(
                        file_path,
                        row_number,
                        "Failed",
                        "Employee creation failed"
                    )

                    print(
                        f"Failed: "
                        f"{first_name} {last_name}"
                    )

                    logger.error(
                        f"Employee creation failed: "
                        f"{first_name} {last_name}"
                    )

                # Wait for OrangeHRM navigation
                page.wait_for_timeout(2000)

            # ==============================================
            # EMPLOYEE EXCEPTION
            # ==============================================

            except Exception as e:

                error_message = str(e)

                failed_records += 1
                screenshot_path = take_screenshot(page,
                    employee_name)

                update_employee_status(
                    file_path,
                    row_number,
                    "Failed",
                    error_message
                )

                print(
                    f"Failed: "
                    f"{first_name} {last_name}"
                )

                print(
                    f"Error: {error_message}"
                )

                logger.error(
                    f"Employee failed: "
                    f"{first_name} {last_name} - "
                    f"{error_message}"
                )
            page.wait_for_timeout(2000)

        # -------------------------------------------------
        # Close browser
        # -------------------------------------------------

        context.close()
        browser.close()

        logger.info(
            "Browser closed successfully"
        )

except Exception as e:

        logger.exception(
        "Critical bot execution failure"
    )

        errors.append(
        f"Critical Bot Error: {str(e)}"
    )


finally:

    # =====================================================
    # EXECUTION END
    # =====================================================

    end_time = datetime.now()

    # -----------------------------------------------------
    # Calculate total processed
    # -----------------------------------------------------

    total_employees = (
        successful_records +
        failed_records
    )

    # -----------------------------------------------------
    # SEND COMPLETION EMAIL
    # -----------------------------------------------------

    send_completion_email(
        start_time=start_time,
        end_time=end_time,
        total_employees=total_employees,
        successful_records=successful_records,
        failed_records=failed_records,
        errors=errors
    )

    logger.info(
        "Completion email sent"
    )

    logger.info(
        "Bot execution completed"
    )


    