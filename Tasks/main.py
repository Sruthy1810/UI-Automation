from playwright.sync_api import sync_playwright
import time
import tkinter as tk
from login import get_login_credentials
from excel_reader import read_employee_data
from employee import create_employee
from logger import logger

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
        
        

        employees = read_employee_data(
            "EmployeeData.xlsx"
        )

        logger.info(f"Employee data read from Excel. Total employees: {len(employees)}")

        for employee in employees:

            # Go to Add Employee page
            page.get_by_role(
                "link",
                name="Add Employee",
                exact=True
            ).click()

            page.get_by_placeholder(
                "First Name"
            ).wait_for(state="visible")

            print("Add Employee page opened")
            logger.info("Add Employee page opened successfully")

            # Create employee
            success = create_employee(
                page,
                employee
            )

            if success:

                print(
                    f"Completed: "
                    f"{employee['First Name']} "
                    f"{employee['Last Name']}"
                )

            else:

                print(
                    f"Failed: "
                    f"{employee['First Name']} "
                    f"{employee['Last Name']}"
                )

            print("Employee created")
            logger.info("Employee Created Successfully")
            # Wait for OrangeHRM to finish navigation
            page.wait_for_timeout(2000)

except Exception as e:

        print("\nPage unable to open")
        print(e)


    