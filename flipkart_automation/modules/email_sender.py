import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from datetime import datetime

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

    except Exception as e:

        print(f"Failed to send trigger email: {e}")





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
    subject="Flipkart Automation - Bot failed"
):
    """
    Sends an HTML email whenever an exception occurs.
    """

    exception_time = datetime.now().strftime(
        "%d-%m-%Y %H:%M:%S"
    )

    if start_time:

        duration = datetime.now() - start_time

    else:

        duration = "N/A"

    # Convert exception to string
    exception_message = str(exception)

    html_body = f"""
<!DOCTYPE html>

<html>

<head>

    <meta charset="UTF-8">

    <style>

        body {{
            font-family: Arial, Helvetica, sans-serif;
            background-color: #f4f6f8;
            margin: 0;
            padding: 30px;
        }}

        .container {{
            max-width: 700px;
            margin: auto;
            background-color: #ffffff;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.10);
        }}

        .header {{
            background-color: #c62828;
            color: white;
            padding: 20px;
            text-align: center;
        }}

        .header h2 {{
            margin: 0;
            font-size: 22px;
        }}

        .content {{
            padding: 25px;
        }}

        .status {{
            background-color: #ffebee;
            border-left: 5px solid #c62828;
            padding: 15px;
            margin-bottom: 20px;
        }}

        .status strong {{
            color: #c62828;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}

        th {{
            background-color: #f1f3f5;
            text-align: left;
            padding: 12px;
            border: 1px solid #ddd;
        }}

        td {{
            padding: 12px;
            border: 1px solid #ddd;
        }}

        .exception {{
            background-color: #fff3f3;
            color: #b71c1c;
            padding: 15px;
            border-radius: 6px;
            margin-top: 20px;
            font-family: Consolas, monospace;
            word-break: break-word;
        }}

        .footer {{
            background-color: #f1f3f5;
            padding: 15px;
            text-align: center;
            color: #666;
            font-size: 12px;
        }}

    </style>

</head>


<body>

    <div class="container">

        <div class="header">

            <h2>
                ⚠ Automation Exception
            </h2>

        </div>


        <div class="content">

            <div class="status">

                <strong>
                    Automation execution failed.
                </strong>

                <br><br>

                An unexpected exception occurred during
                the automation process.

            </div>


            <table>

                <tr>
                    <th>Bot Name</th>
                    <td>{bot_name}</td>
                </tr>

                <tr>
                    <th>Exception Time</th>
                    <td>{exception_time}</td>
                </tr>

                <tr>
                    <th>Execution Duration</th>
                    <td>{duration}</td>
                </tr>

            </table>


            <h3>
                Exception Details
            </h3>


            <div class="exception">

                {exception_message}

            </div>

        </div>


        <div class="footer">

            Flipkart Automation Bot<br>

            Automated Exception Notification

        </div>

    </div>

</body>

</html>
"""

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