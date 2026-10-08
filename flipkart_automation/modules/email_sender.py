import os
import html
import smtplib
import traceback
from datetime import datetime
from email.message import EmailMessage
from email.utils import formataddr
import re
from utils.logger import logger, get_log_file

from config.config_reader import (
    get_smtp_server,
    get_smtp_port,
    get_sender_email,
    get_sender_password,
    get_receiver_email
)



def _send(message):
    """Send one prepared EmailMessage through SMTP."""
    with smtplib.SMTP(get_smtp_server(), get_smtp_port()) as server:
        server.starttls()
        server.login(get_sender_email(), get_sender_password())
        server.send_message(message)


def _pick(product, *keys, default="N/A"):
    """Return the first non-empty value among several possible key spellings."""
    for key in keys:
        value = product.get(key)
        if value not in (None, ""):
            return value
    return default


# -----------------------------------------
# TRIGGER MAIL
# -----------------------------------------
def send_trigger_email(total_products):

    msg = EmailMessage()
    msg["Subject"] = "Flipkart Automation - Bot Started"
    msg["From"] = get_sender_email()
    msg["To"] = get_receiver_email()

    start_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    body = f"""
Hello,

The Flipkart automation bot has been triggered successfully.

Bot Name : Flipkart Automation
Start Time : {start_time}
Total Products : {total_products}


The automation process has started.

Thanks & Regards,
Automation Bot
"""
    msg.set_content(body)

    try:
        _send(msg)
        print("Trigger email sent successfully.")
        logger.info("Trigger email sent successfully.")
    except Exception as e:
        print(f"Failed to send trigger email: {e}")
        logger.error(f"Failed to send trigger email: {e}")


# -----------------------------------------
# PRODUCT MAIL (one per product, after the cart step)
# -----------------------------------------

_sent_mails = set()   # (url, status) pairs already mailed in this run


def _clean_price(value):
    """'₹3,99981% off' -> '₹3,999'. Returns '' if no price is found."""
    if value is None:
        return ""
    m = re.search(r"₹\s?\d{1,3}(?:,\d{2,3})*(?:\.\d+)?", str(value))
    return m.group(0).replace(" ", "") if m else ""

def send_product_email(
    product,
    cart_status="Success",
    remarks="",            # kept so old calls don't break; NOT shown in the mail
    size=None,
    search_term=None,
    to_email=None
):
    """
    Send ONE email for ONE product, with its cart status.
    Remarks are not included here (they are written to Excel only).
    Never raises, so it can't stop the bot.
    """
    # Accept a list too, so older calls like send_product_email(products) still work
    if isinstance(product, list):
        if not product:
            logger.warning("No product to email.")
            return
        product = product[0]

    if not product:
        logger.warning("No product found. Email not sent.")
        return

    try:
        raw_url = str(_pick(product, "url", "URL", "link", default="") or "")
        status = str(cart_status).strip().lower()

        is_success = status == "success"
        is_out_of_stock = status in ("out_of_stock", "out of stock")

        # Duplicate guard: same product + same status is mailed only once per run
        key = (raw_url, status)
        if raw_url and key in _sent_mails:
            logger.info(f"Product email already sent, skipping: {raw_url}")
            return

        raw_name = str(_pick(product, "name", "Name", "title", default="Product"))
        name = html.escape(raw_name)
        price = html.escape(str(_pick(product, "price", "Price", default="N/A")))
        rating = html.escape(str(_pick(product, "rating", "Rating", default="N/A")))
        url = html.escape(raw_url, quote=True)
        image = html.escape(str(_pick(product, "image", "Image", default="") or ""), quote=True)

        if is_success:
            status_color = "#2e7d32"
            status_text = "Added to cart"
            subject_status = "Added to cart"

        elif is_out_of_stock:
            status_color = "#ef6c00"
            status_text = "Product is out of stock"
            subject_status = "Out of Stock"

        else:
            status_color = "#c62828"
            status_text = "Could not add to cart"
            subject_status = "Cart failed"

        rows = ""
        if search_term:
            rows += f"<p><b>Searched for:</b> {html.escape(str(search_term))}</p>"
        if size:
            rows += f"<p><b>Size:</b> {html.escape(str(size))}</p>"
        rows += f"<p><b>Name:</b> {name}</p>"
        rows += f"<p><b>Price:</b> {price}</p>"
        rows += f"<p><b>Rating:</b> {rating}</p>"

        image_tag = (
            f'<img src="{image}" width="200" height="200" style="object-fit:contain;">'
            if image else ""
        )
        link_tag = f'<p><a href="{url}">View Product</a></p>' if url else ""

        html_content = f"""
        <html>
        <body style="font-family:Arial, sans-serif;">
            <h2>Flipkart Product Recommendation</h2>
            <div style="border:1px solid #cccccc; padding:15px; width:600px;">
                <p style="font-size:16px; font-weight:bold; color:{status_color};">
                    {status_text}
                </p>
                {image_tag}
                {rows}
                {link_tag}
            </div>
        </body>
        </html>
        """

        message = EmailMessage()
        message["From"] = formataddr(("Flipkart Automation Bot", get_sender_email()))
        message["To"] = to_email or get_receiver_email()
        message["Subject"] = (
            f"Flipkart Product Recommendation - {search_term or raw_name}"
            f" ({subject_status})"
        )
        message.set_content(
            f"{status_text}\n\n"
            f"Name: {raw_name}\n"
            f"Price: {_pick(product, 'price', 'Price', default='N/A')}\n"
            f"URL: {raw_url}"
        )
        message.add_alternative(html_content, subtype="html")

        _send(message)

        if raw_url:
            _sent_mails.add(key)

        logger.info(f"Product email sent for: {search_term or raw_name} ({cart_status})")

    except Exception as e:
        logger.error(f"Failed to send product email: {e}")


# -----------------------------------------
# EXCEPTION MAIL
# -----------------------------------------
def send_exception_email(
    exception,
    start_time=None,
    bot_name="Flipkart Automation",
    subject="Flipkart Automation - Bot failed",
    screenshot_path=None
):
    """Sends an HTML email whenever an exception occurs. Never raises."""
    try:
        exception_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        duration = str(datetime.now() - start_time) if start_time else "N/A"

        error_type = type(exception).__name__
        error_message = str(exception)

        # Keep the original exception object; only escape the text
        if isinstance(exception, BaseException):
            trace_text = "".join(
                traceback.format_exception(type(exception), exception, exception.__traceback__)
            )
        else:
            trace_text = error_message

        error_message_html = html.escape(error_message)
        trace_html = html.escape(trace_text)

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
    <div class="header"><h2>&#9888; Automation Exception</h2></div>
    <div class="content">
        <table>
            <tr><th>Bot Name</th><td>{html.escape(bot_name)}</td></tr>
            <tr><th>Exception Time</th><td>{exception_time}</td></tr>
            <tr><th>Execution Duration</th><td>{duration}</td></tr>
            <tr><th>Error Type</th><td>{html.escape(error_type)}</td></tr>
            <tr><th>Error Message</th><td>{error_message_html}</td></tr>
        </table>
        <div class="exception"></div>
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
        message.set_content(f"{bot_name} failed at {exception_time}\n\n{error_message}")
        message.add_alternative(html_body, subtype="html")

        # Attach failure screenshot
        if screenshot_path and os.path.exists(screenshot_path):
            with open(screenshot_path, "rb") as f:
                message.add_attachment(
                    f.read(),
                    maintype="image",
                    subtype="png",
                    filename=os.path.basename(screenshot_path)
                )

        _send(message)
        print("Exception email sent successfully.")

    except Exception as mail_error:
        print(f"Failed to send exception email: {mail_error}")


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
        error_text = "\n".join(f"- {error}" for error in errors)
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

    # Attach execution log file
    try:
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
        _send(msg)
        print("Execution email sent successfully.")
    except Exception as e:
        print(f"Failed to send execution email: {e}")