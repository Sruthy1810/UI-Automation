from playwright.sync_api import sync_playwright
import time
import tkinter as tk
from login import get_login_credentials
from excel_reader import read_employee_data,update_employee_status
from employee import create_employee
from logger import logger
from pathlib import Path




#   PROJECT PATH   #

base_dir = Path(__file__).resolve().parent

file_path = base_dir / "EmployeeData.xlsx"



#screen size
root = tk.Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.destroy()

try:
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
        

        logger.info(f"Employee data read from Excel. Total employees: {len(employees)}")


        for employee in employees:

            row_number = employee["_row_number"]

            first_name = str(
                employee["First Name"]
            ).strip()

            last_name = str(
                employee["Last Name"]
            ).strip()

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

except Exception as e:

        print("\nPage unable to open")
        print(e)


    