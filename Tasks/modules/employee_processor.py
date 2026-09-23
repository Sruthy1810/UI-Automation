from modules.excel_reader import (
    read_employee_data,
    update_employee_status
)

from modules.employee import create_employee
from utils.screenshot import take_screenshot
from utils.logger import logger


def process_employees(page, file_path):

    successful_records = 0
    failed_records = 0
    errors = []

    employees = read_employee_data(file_path)

    logger.info(
        f"Employee data read from Excel. "
        f"Total employees: {len(employees)}"
    )

    for employee in employees:

        # =================================================
        # CHECK PROCESSING STATUS
        # =================================================

        processing_status = str(
            employee.get("Processing Status", "")
        ).strip().lower()

        if processing_status == "completed":

            first_name = str(
                employee["First Name"]
            ).strip()

            last_name = str(
                employee["Last Name"]
            ).strip()

            employee_name = f"{first_name} {last_name}"

            logger.info(
                f"Skipping {employee_name} - "
                f"Already Completed"
            )

            print(
                f"Skipping {employee_name} - "
                f"Already Completed"
            )

            continue

    # =================================================
    # PROCESS EMPLOYEE
    # =================================================

        row_number = employee["_row_number"]

        first_name = str(
            employee["First Name"]
        ).strip()

        last_name = str(
            employee["Last Name"]
        ).strip()

        employee_name = f"{first_name} {last_name}"

        # =================================================
        # RETRY EMPLOYEE - MAXIMUM 2 ATTEMPTS
        # =================================================

        employee_success = False
        last_error = None

        for attempt in range(1, 3):

            try:

                logger.info(
                    f"Processing {employee_name} "
                    f"- Attempt {attempt}/2"
                )

                print(
                    f"\nCreating employee: {employee_name}"
                )

                print(
                    f"Attempt {attempt}/2"
                )

                # -----------------------------------------
                # Open Add Employee
                # -----------------------------------------

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

                logger.info(
                    f"Add Employee page opened for "
                    f"{employee_name}"
                )

                # -----------------------------------------
                # Create Employee
                # -----------------------------------------

                success = create_employee(
                    page,
                    employee
                )

                # =========================================
                # SUCCESS
                # =========================================

                if success:

                    update_employee_status(
                        file_path,
                        row_number,
                        "Success",
                        "Employee created and document uploaded successfully"
                    )

                    successful_records += 1
                    employee_success = True

                    logger.info(
                        f"Employee created successfully: "
                        f"{employee_name}"
                    )

                    print(
                        f"{employee_name} completed successfully"
                    )

                    break

                # =========================================
                # CREATE_EMPLOYEE RETURNED FALSE
                # =========================================

                else:

                    last_error = (
                        "Employee creation returned False"
                    )

                    logger.error(
                        f"Employee creation returned False: "
                        f"{employee_name} "
                        f"- Attempt {attempt}/2"
                    )

                    # -------------------------------------
                    # TAKE SCREENSHOT
                    # -------------------------------------

                    try:

                        logger.info(
                            f"Taking failure screenshot: "
                            f"{employee_name} "
                            f"- Attempt {attempt}"
                        )

                        screenshot_path = take_screenshot(
                            page,
                            f"{employee_name}_attempt_{attempt}"
                        )

                        logger.info(
                            f"Failure screenshot saved: "
                            f"{screenshot_path}"
                        )

                        print(
                            f"Failure screenshot saved: "
                            f"{screenshot_path}"
                        )

                    except Exception as screenshot_error:

                        logger.error(
                            f"Screenshot failed for "
                            f"{employee_name}: "
                            f"{screenshot_error}"
                        )

            # =============================================
            # UNEXPECTED EXCEPTION
            # =============================================

            except Exception as e:

                last_error = str(e)

                logger.exception(
                    f"Employee failed: "
                    f"{employee_name} "
                    f"- Attempt {attempt}/2"
                )

                print(
                    f"{employee_name} failed "
                    f"on attempt {attempt}: {e}"
                )

                # -----------------------------------------
                # TAKE SCREENSHOT FOR EXCEPTION
                # -----------------------------------------

                try:

                    logger.info(
                        f"Taking exception screenshot: "
                        f"{employee_name} "
                        f"- Attempt {attempt}"
                    )

                    screenshot_path = take_screenshot(
                        page,
                        f"{employee_name}_attempt_{attempt}"
                    )

                    logger.info(
                        f"Exception screenshot saved: "
                        f"{screenshot_path}"
                    )

                    print(
                        f"Exception screenshot saved: "
                        f"{screenshot_path}"
                    )

                except Exception as screenshot_error:

                    logger.error(
                        f"Screenshot failed for "
                        f"{employee_name}: "
                        f"{screenshot_error}"
                    )

            # =============================================
            # RETRY
            # =============================================

            if not employee_success and attempt < 2:

                logger.warning(
                    f"Retrying employee: "
                    f"{employee_name}"
                )

                print(
                    f"Retrying {employee_name}..."
                )

                page.wait_for_timeout(2000)

        # =================================================
        # FINAL RESULT AFTER 2 ATTEMPTS
        # =================================================

        if not employee_success:

            failed_records += 1

            errors.append(
                f"{employee_name}: {last_error}"
            )

            update_employee_status(
                file_path,
                row_number,
                "Failed",
                f"Failed after 2 attempts: {last_error}"
            )

            logger.error(
                f"Employee permanently failed: "
                f"{employee_name}"
            )

        # -----------------------------------------
        # Wait before next employee
        # -----------------------------------------

        page.wait_for_timeout(2000)

    # =================================================
    # RETURN ACTUAL VALUES
    # =================================================

    return (
        len(employees),
        successful_records,
        failed_records,
        errors
    )
