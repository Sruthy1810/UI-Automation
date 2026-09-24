import configparser
import socket
import getpass
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from email.mime.base import MIMEBase
from email import encoders


# ---------------------------------------------------------
# Read email configuration
# ---------------------------------------------------------

config = configparser.ConfigParser()
config.read("config.ini")

SMTP_SERVER = config["EMAIL"]["smtp_server"]
SMTP_PORT = int(config["EMAIL"]["smtp_port"])

SENDER_EMAIL = config["EMAIL"]["sender_email"]
SENDER_PASSWORD = config["EMAIL"]["sender_password"]

RECEIVER_EMAIL = config["EMAIL"]["receiver_email"]

BOT_NAME = config["EMAIL"]["bot_name"]


# ---------------------------------------------------------
# Get machine name
# ---------------------------------------------------------

def get_machine_name():

    return socket.gethostname()


# ---------------------------------------------------------
# Get current Windows username
# ---------------------------------------------------------

def get_user_name():

    return getpass.getuser()


# ---------------------------------------------------------
# Send email
# ---------------------------------------------------------

def send_email(subject, body,attachment_file=None):

    try:

        message = MIMEMultipart()

        message["From"] = SENDER_EMAIL
        message["To"] = RECEIVER_EMAIL
        message["Subject"] = subject

        message.attach(
            MIMEText(body, "plain")
        )

        # -----------------------------------------
        # Attachment
        # -----------------------------------------

        if attachment_file:

            if os.path.exists(attachment_file):

                with open(
                    attachment_file,
                    "rb"
                ) as file:

                    attachment = MIMEBase(
                        "application",
                        "octet-stream"
                    )

                    attachment.set_payload(
                        file.read()
                    )

                encoders.encode_base64(
                    attachment
                )

                attachment.add_header(
                    "Content-Disposition",
                    f'attachment; filename="{os.path.basename(attachment_file)}"'
                )

                message.attach(attachment)

                print(
                    f"Attachment added: {attachment_file}"
                )

            else:

                print(
                    f"Attachment not found: {attachment_file}"
                )

        # -----------------------------------------
        # Send Email
        # -----------------------------------------


        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:

            server.starttls()

            server.login(
                SENDER_EMAIL,
                SENDER_PASSWORD
            )

            server.sendmail(
                SENDER_EMAIL,
                RECEIVER_EMAIL,
                message.as_string()
            )

        print("Email sent successfully")

        return True

    except Exception as e:

        print(f"Email sending failed: {e}")

        return False


# ---------------------------------------------------------
# Bot Start Email
# ---------------------------------------------------------

def send_start_email(start_time):

    machine_name = get_machine_name()
    user_name = get_user_name()

    subject = f"{BOT_NAME} - Execution Started"

    body = f"""
Bot Execution Started

Bot Name        : {BOT_NAME}
Execution Date  : {start_time.strftime("%d-%m-%Y")}
Execution Time  : {start_time.strftime("%H:%M:%S")}
Machine Name    : {machine_name}
User Name       : {user_name}

The bot execution has started successfully.
"""

    return send_email(subject, body)


# ---------------------------------------------------------
# Bot Completion Email
# ---------------------------------------------------------

def send_completion_email(
    start_time,
    end_time,
    total_employees,
    successful_records,
    failed_records,
    errors,
    execution_log_file
):


    print("========================================")
    print("COMPLETION EMAIL FUNCTION STARTED")
    print("========================================")

    print("Total:", total_employees)
    print("Success:", successful_records)
    print("Failed:", failed_records)
    print("Errors:", errors)
    print("Execution Log:", execution_log_file)

    #total_employees = int(total_employees)
    #successful_records = int(successful_records)
    #failed_records = int(failed_records)


    machine_name = get_machine_name()
    user_name = get_user_name()

    duration = end_time - start_time

    # Determine execution status

    if failed_records == 0 and not errors:
        execution_status = "Success"

    elif successful_records > 0 and failed_records > 0:
        execution_status = "Partial"

    else:
        execution_status = "Failed"

    # Error summary

    if errors:

        error_summary = "\n".join(
            f"- {error}"
            for error in errors
        )

    else:

        error_summary = "No errors"

    subject = f"{BOT_NAME} - Execution Completed"

    body = f"""
Bot Execution Completed

Bot Name        : {BOT_NAME}
Machine Name    : {machine_name}
User Name       : {user_name}

--------------------------------------------------
EXECUTION SUMMARY
--------------------------------------------------

Total Employees Processed : {total_employees}
Successful Records        : {successful_records}
Failed Records            : {failed_records}

Execution Start Time      : {start_time.strftime("%d-%m-%Y %H:%M:%S")}
Execution End Time        : {end_time.strftime("%d-%m-%Y %H:%M:%S")}

Total Execution Duration  : {duration}

--------------------------------------------------
ERROR SUMMARY
--------------------------------------------------

{error_summary}

--------------------------------------------------
EXECUTION STATUS
--------------------------------------------------

{execution_status}

The bot execution process has been completed.
"""

    return send_email(subject, body, execution_log_file)