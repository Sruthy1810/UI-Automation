from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from utils.logger import logger


def login_to_orangehrm(page, username, password):

    try:

        page.locator(
            'input[name="username"]'
        ).fill(username)

        page.locator(
            'input[name="password"]'
        ).fill(password)

        page.locator(
            'button[type="submit"]'
        ).click()

        page.wait_for_load_state(
            "domcontentloaded"
        )

        page.get_by_text(
            "PIM",
            exact=True
        ).wait_for(
            state="visible",
            timeout=10000
        )

        logger.info(
            "OrangeHRM login successful"
        )

    except PlaywrightTimeoutError:

        logger.exception(
            "OrangeHRM login failed"
        )

        raise


def open_pim(page):

    page.get_by_text(
        "PIM",
        exact=True
    ).click()

    page.get_by_role(
        "link",
        name="Add Employee",
        exact=True
    ).wait_for(
        state="visible"
    )

    logger.info(
        "PIM page opened successfully"
    )


def open_add_employee(page):

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
        "Add Employee page opened"
    )