from playwright.async_api import TimeoutError 
import tkinter as tk
from tkinter import simpledialog
from config.config_reader import get_session_file
from utils.logger import logger

def get_otp_from_popup():
    """
    Opens a Tkinter popup and gets OTP from the user.
    """

    root = tk.Tk()
    root.withdraw()

    otp = simpledialog.askstring(
        "Flipkart OTP",
        "Enter the OTP received on your phone:"
    )

    root.destroy()

    if not otp:
        raise ValueError("OTP was not entered.")

    return otp.strip()


async def open_flipkart(
    page,
    context,
    login_type,
    phone_number,
    email
):

    try:

        # --------------------------------
        # Check Login
        # --------------------------------

        login_button = page.get_by_text(
            "Login",
            exact=True
        )

        try:

            await login_button.wait_for(
                state="visible",
                timeout=3000
            )

        except TimeoutError:

            print("Already logged in.")
            return True

        # --------------------------------
        # Login required
        # --------------------------------

        print("Login required.")

        await login_button.click()

        # --------------------------------
        # Login based on type
        # --------------------------------

        if login_type.lower() == "phone":

            print("Login type: Phone")

            phone_input = page.locator(
                "input[type='number'], input[type='tel']"
            ).first

            await phone_input.wait_for(
                state="visible",
                timeout=5000
            )

            await phone_input.fill(
                phone_number
            )

            print("Phone number entered.")

        elif login_type.lower() == "email":

            print("Login type: Email")

            email_input = page.locator(
                "input[type='text'], input[type='email']"
            ).first

            await email_input.wait_for(
                state="visible",
                timeout=5000
            )

            await email_input.fill(
                email
            )

            print("Email entered.")

        else:

            raise ValueError(
                "Invalid LOGIN_TYPE. "
                "Use 'phone' or 'email'."
            )

        # --------------------------------
        # Continue
        # --------------------------------

        continue_button = page.get_by_role(
            "button",
            name="Continue"
        )

        await continue_button.wait_for(
            state="visible",
            timeout=5000
        )

        await continue_button.click()

        logger.info("Continue button clicked.")

        # --------------------------------
        # Wait for OTP
        # --------------------------------

        print("Waiting for OTP...")

        await page.wait_for_timeout(1000)

        # --------------------------------
        # OTP Popup
        # --------------------------------

        otp = get_otp_from_popup()

        print("OTP received from popup.")

        # --------------------------------
        # Enter OTP into 6 OTP fields
        # --------------------------------

        otp_inputs = page.locator(
            "input.S1KmoO[type='number']"
        )

        await otp_inputs.first.wait_for(
            state="visible",
            timeout=5000
        )

        count = await otp_inputs.count()

        if count != 6:
            raise Exception(
                f"Expected 6 OTP fields, but found {count}"
            )

        if len(otp) != 6 or not otp.isdigit():
            raise ValueError(
                "OTP must contain exactly 6 digits."
            )

        # Enter each OTP digit into each field
        for i, digit in enumerate(otp):

            await otp_inputs.nth(i).fill(digit)

        print("OTP entered successfully.")

        # --------------------------------
        # Continue after OTP
        # --------------------------------

        try:

            await page.get_by_role(
                "button",
                name="Verify"
            ).click(
                timeout=5000
            )

            logger.info(
                "OTP Continue button clicked."
            )

        except TimeoutError:
            logger.error("OTP Continue button not found.")
            print(
                "OTP Continue button not found. "
                "Checking login status."
            )

        # --------------------------------
        # Wait for Login Completion
        # --------------------------------

        await page.wait_for_timeout(3000)

        print(
            "Flipkart login process completed."
        )

        await save_session(context)

        return True

    except Exception as e:

        logger.error("Login failed")
        print(f"Login failed: {e}")

        raise


async def save_session(context):

    session_file = get_session_file()

    session_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    await context.storage_state(
        path=str(session_file)
    )

    print(
        f"Session saved: {session_file}"
    )