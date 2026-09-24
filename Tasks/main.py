from datetime import datetime

from config.config_reader import get_employee_file_path

from modules.login import get_login_credentials_from_popup
from modules.bot_runner import run_bot

from utils.email_notification import (
    send_start_email,
    send_completion_email
)
from utils.execution_log import (
    start_execution_log,
    create_execution_log
)

from utils.excel_formatter import color_failed_rows
from utils.logger import logger


def main():

    execution_log_file = None

    # -----------------------------------------
    # Login Popup
    # -----------------------------------------

    username, password = get_login_credentials_from_popup()

    if not username or not password:

        logger.info("Login cancelled by user")

        return

    # -----------------------------------------
    # Start Execution
    # -----------------------------------------

    start_time = datetime.now()

    # -----------------------------------------
    # Capture Log Starting Position
    # -----------------------------------------

    execution_start = start_execution_log()

    # -----------------------------------------
    # Start Email
    # -----------------------------------------

    send_start_email(start_time)

    # -----------------------------------------
    # Employee Excel
    # -----------------------------------------

    file_path = get_employee_file_path()

    try:

        total_employees, successful_records, failed_records, errors = run_bot(
            file_path,
            username,
            password
        )

        print("Bot execution completed")
        # -----------------------------------------
        # Format Failed Excel Rows
        # -----------------------------------------

        try:
            color_failed_rows(file_path)

            logger.info(
                "Failed employee rows formatted successfully"
            )
        

        except Exception as e:

            logger.exception(
                "Excel formatting failed"
            )

            errors.append(
                f"Excel formatting error: {str(e)}"
            )
       
        # -----------------------------------------
        # End Execution
        # -----------------------------------------

        end_time = datetime.now()

        # -----------------------------------------
        # Create Current Execution Log
        # -----------------------------------------

        execution_log_file = create_execution_log(
            execution_start
        )

        # -----------------------------------------
        # Completion Email
        # -----------------------------------------
        
        print("Sending completion email...")
        
        email_status = send_completion_email(
                start_time,
                end_time,
                total_employees,
                successful_records,
                failed_records,
                errors,
                execution_log_file        
            )
        
        print(
         "Completion email status:",
            email_status
            )    

    except Exception as e:

        logger.exception(
            "Bot execution failed"
        )

        end_time = datetime.now()

        print("BOT ERROR:", e)

        # -----------------------------------------
        # Create Current Execution Log
        # Even when bot fails
        # -----------------------------------------

        execution_log_file = create_execution_log(
            execution_start
        )

        # -----------------------------------------
        # Failure Completion Email
        # -----------------------------------------

        print("Sending failure completion email...")

        send_completion_email(
            start_time,
            end_time,
            0,
            0,
            0,
            [str(e)],
            execution_log_file
        )


if __name__ == "__main__":
    main()