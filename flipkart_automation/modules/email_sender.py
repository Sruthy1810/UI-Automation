import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from datetime import datetime
import html
from sys import exception
import traceback
from utils.logger import logger,get_log_file 
import os

from config.config_reader import (
    get_smtp_server,
    get_smtp_port,
    get_sender_email,
    get_sender_password,
    get_receiver_email
)


def send_trigger_email():

    msg = EmailMessage()

    msg["Subject"] = "Flipkart Automation - Bot Started"
    msg["From"] = get_sender_email()
    msg["To"] = get_receiver_email()

    start_time = datetime.now().strftime(
        "%d-%m-%Y %H:%M:%S"
    )

    body = f"""
Hello,

The Flipkart automation bot has been triggered successfully.

Bot Name : Flipkart Automation
Start Time : {start_time}

The automation process has started.

Thanks & Regards,
Automation Bot
"""

    msg.set_content(body)

    try:

        with smtplib.SMTP(
            get_smtp_server(),
            get_smtp_port()
        ) as server:

            server.starttls()

            server.login(
                get_sender_email(),
                get_sender_password()
            )

            server.send_message(msg)

        print("Trigger email sent successfully.")
        logger.info("Trigger email sent successfully.")

    except Exception as e:

        print(f"Failed to send trigger email: {e}")
        logger.error(f"Failed to send trigger email: {e}")





def send_product_email(products):

    if not products:
        print("No products found. Email not sent.")
        return

    # -----------------------------------------
    # Read email configuration
    # -----------------------------------------


    smtp_server = get_smtp_server()
    smtp_port = get_smtp_port()
    sender_email = get_sender_email()
    sender_password = get_sender_password()
    receiver_email = get_receiver_email()



    
    # -----------------------------------------
    # Email subject
    # -----------------------------------------

    subject = "Flipkart Product Recommendations"

    # -----------------------------------------
    # Create HTML
    # -----------------------------------------

    html_content = """
    <html>
    <body>

        <h2>Flipkart Product Recommendations</h2>

        <p>
            Here are the selected products based on the applied filters.
        </p>
    """

    for index, product in enumerate(products, start=1):

        name = product.get("name", "N/A")
        price = product.get("price", "N/A")
        rating = product.get("rating", "N/A")
        url = product.get("url", "")
        image = product.get("image", "")

        html_content += f"""
        <div style="
            border: 1px solid #cccccc;
            padding: 15px;
            margin-bottom: 20px;
            width: 600px;
        ">

            <h3>Product {index}</h3>

            <img src="{image}"
                 width="200"
                 height="200"
                 style="object-fit:contain;">

            <p>
                <b>Name:</b> {name}
            </p>

            <p>
                <b>Price:</b> {price}
            </p>

            <p>
                <b>Rating:</b> {rating}
            </p>

            <p>
                <a href="{url}">
                    View Product
                </a>
            </p>

        </div>
        """

    html_content += """
    </body>
    </html>
    """

    # -----------------------------------------
    # Create email
    # -----------------------------------------

    message = EmailMessage()

    message["From"] = formataddr(
        ("Flipkart Automation Bot", sender_email)
    )

    message["To"] = receiver_email
    message["Subject"] = subject

    message.set_content(
        "Please open this email in HTML format to view the product details."
    )

    message.add_alternative(
        html_content,
        subtype="html"
    )

    # -----------------------------------------
    # Send email
    # -----------------------------------------

    try:

        with smtplib.SMTP(
            smtp_server,
            smtp_port
        ) as server:

            server.starttls()

            server.login(
                sender_email,
                sender_password
            )

            server.send_message(message)

        print(
            f"Product email sent successfully to: "
            f"{receiver_email}"
        )

    except Exception as e:

        print(f"Failed to send product email: {e}")


    # -----------------------------------------
    #   EXCEPTION MAIL
    # -----------------------------------------


def send_exception_email(
    exception,
    start_time=None,
    bot_name="Flipkart Automation",
    subject="Flipkart Automation - Bot failed",
    screenshot_path=None
):
    """
    Sends an HTML email whenever an exception occurs.
    """

    try:
                exception_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                duration = str(datetime.now() - start_time) if start_time else "N/A"

                error_type = type(exception).__name__
                exception_message = html.escape(str(exception))
                trace = html.escape(traceback.format_exc())

                html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; background:#f4f6f8; padding:30px; }}
            .container {{ max-width:700px; margin:auto; background:#fff; border-radius:10px;
                        overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,0.10); }}
            .header {{ background:#c62828; color:#fff; padding:20px; text-align:center; }}
            .content {{ padding:25px; }}
            table {{ width:100%; border-collapse:collapse; margin-top:15px; }}
            th {{ background:#f1f3f5; text-align:left; padding:12px; border:1px solid #ddd; }}
            td {{ padding:12px; border:1px solid #ddd; }}
            .exception {{ background:#fff3f3; color:#b71c1c; padding:15px; border-radius:6px;
                        margin-top:15px; font-family:Consolas, monospace;
                        white-space:pre-wrap; word-break:break-word; }}
            .footer {{ background:#f1f3f5; padding:15px; text-align:center;
                    color:#666; font-size:12px; }}
        </style>
        </head>
        <body>
        <div class="container">
            <div class="header"><h2>⚠ Automation Exception</h2></div>
            <div class="content">
                <table>
                    <tr><th>Bot Name</th><td>{bot_name}</td></tr>
                    <tr><th>Exception Time</th><td>{exception_time}</td></tr>
                    <tr><th>Execution Duration</th><td>{duration}</td></tr>
                    <tr><th>Error Type</th><td>{error_type}</td></tr>
                </table>

                <h3>Exception Details</h3>
                <div class="exception">{exception_message}</div>

                <h3>Traceback</h3>
                <div class="exception">{trace}</div>
            </div>
            <div class="footer">
                Flipkart Automation Bot<br>Automated Exception Notification
            </div>
        </div>
        </body>
        </html>
        """

                message = EmailMessage()
                message["From"] = formataddr(("Flipkart Automation Bot", get_sender_email()))
                message["To"] = get_receiver_email()
                message["Subject"] = subject
                message.set_content(f"{bot_name} failed at {exception_time}\n\n{exception}")
                message.add_alternative(html_body, subtype="html")

                 # Attach failure screenshot
                if screenshot_path:
                    import os
                    if os.path.exists(screenshot_path):
                        with open(screenshot_path, "rb") as f:
                            message.add_attachment(
                                f.read(),
                                maintype="image",
                                subtype="png",
                                filename=os.path.basename(screenshot_path)
                            )

                

                with smtplib.SMTP(get_smtp_server(), get_smtp_port()) as server:
                    server.starttls()
                    server.login(get_sender_email(), get_sender_password())
                    server.send_message(message)

                print("Exception email sent successfully.")

    except Exception as mail_error:
            print(f"Failed to send exception email: {mail_error}")

    #send_exception_email(
     #   subject="Flipkart Automation - Bot failed",
     #   html_body=html_body
    #)

    # -----------------------------------------
    # EXECUTION MAIL
    # -----------------------------------------


def send_execution_email(
    start_time,
    end_time,
    total_products,
    successful_products,
    failed_products,
    errors=None
):

    msg = EmailMessage()

    msg["Subject"] = "Flipkart Automation - Execution Report"
    msg["From"] = get_sender_email()
    msg["To"] = get_receiver_email()

    duration = end_time - start_time

    if errors:
        error_text = "\n".join(
            f"- {error}" for error in errors
        )
    else:
        error_text = "No errors"

    if failed_products == 0:
        status = "SUCCESS"
    elif successful_products > 0:
        status = "PARTIAL"
    else:
        status = "FAILED"

    body = f"""
Hello,

Flipkart automation execution has been completed.

==============================
EXECUTION REPORT
==============================

Bot Name       : Flipkart Automation

Start Time     : {start_time.strftime("%d-%m-%Y %H:%M:%S")}
End Time       : {end_time.strftime("%d-%m-%Y %H:%M:%S")}
Duration       : {duration}

Total Products : {total_products}
Successful     : {successful_products}
Failed         : {failed_products}

Execution Status : {status}

Errors:
{error_text}

==============================

Thanks & Regards,
Automation Bot
"""

    msg.set_content(body)

   # -----------------------------------------
    # Attach execution log file
    # -----------------------------------------
    try:
        # Flush buffered log lines to disk before reading
        for h in logger.handlers:
            h.flush()

        log_file_path = get_log_file()

        if os.path.exists(log_file_path):
            with open(log_file_path, "rb") as f:
                msg.add_attachment(
                    f.read(),
                    maintype="text",
                    subtype="plain",
                    filename=os.path.basename(log_file_path)
                )
        else:
            print(f"Log file not found, skipping attachment: {log_file_path}")

    except Exception as e:
        print(f"Could not attach log file: {e}")

    try:

        with smtplib.SMTP(
            get_smtp_server(),
            get_smtp_port()
        ) as server:

            server.starttls()

            server.login(
                get_sender_email(),
                get_sender_password()
            )

            server.send_message(msg)

        print("Execution email sent successfully.")

    except Exception as e:

        print(f"Failed to send execution email: {e}")