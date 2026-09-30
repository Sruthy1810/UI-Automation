from browser.browser_manager import start_browser
from config.config_reader import (get_flipkart_url,get_email,get_login_type,get_phonenumber)
from utils.logger import logger
from modules.login import open_flipkart
from modules.excel_reader import read_products
from modules.flipkart_actions import (
    search_product,
    apply_price_filter,
    apply_rating_filter,
    get_products
)
from modules.email_sender import (send_trigger_email,
                                  send_execution_email,
                                   send_product_email,
                                   send_exception_email)
from datetime import datetime

from modules.retry import retry_async

async def run_bot():

    logger.info("BOT RUNNER STARTED")
    print("BOT RUNNER STARTED")

    start_time = datetime.now()

    successful_products = 0
    failed_products = 0

    errors = []

    playwright = None
    browser = None
    context = None
    page = None



    try:

        # -----------------------------------------
        # Start browser
        # -----------------------------------------


        playwright, browser, context, page = await start_browser()

        # ==========================================
        # TRIGGER EMAIL
        # ==========================================

        send_trigger_email()

        logger.info("Trigger email sent.")

    
            # --------------------------------
            # Get configuration
            # --------------------------------


        url = get_flipkart_url()
        login_type = get_login_type()
        phone_number = get_phonenumber()
        email = get_email()    

            # --------------------------------
            # Open Flipkart
            # --------------------------------

        logger.info("Opening Flipkart...")


        await page.goto(
            url,
            wait_until="domcontentloaded"
        )

        logger.info("Flipkart opened successfully")


        # ------------------------------------------------#
        #                 LOGIN                           #
        # ------------------------------------------------#
        
        logger.info("Logging into flipkart")

        await open_flipkart(    
            page,
            context,
            login_type,
            phone_number,
            email
        )

        # --------------------------------
        # Read Excel
        # --------------------------------

        excel_products = read_products()

        total_products = len(excel_products)

        logger.info(
            f"Products found in Excel: {total_products}"
        )


        #print(f"Products received: {products}")
        # --------------------------------
        # Process Products
        # --------------------------------   

        for product_data in excel_products:

            try:

                product = product_data["Product"]
                price = product_data["Price"]
                rating = product_data["Customer Ratings"]

                logger.info("\n" + "=" * 50)
                logger.info(f"Processing Product : {product}")
                logger.info(f"Maximum Price      : {price}")
                logger.info(f"Customer Rating    : {rating}")
                logger.info("=" * 50)

                # --------------------------------
                # Search Product
                # --------------------------------

                await retry_async(
                    search_product,
                    page,
                    product,
                    action_name=f"Search {product}"
                )

            # --------------------------------
            # Apply Maximum Price Filter
            # --------------------------------

                await retry_async(
                    apply_price_filter,
                    page,
                    price,
                    action_name="Price Filter"
                 )

            # --------------------------------
            # Apply Rating Filter
            # --------------------------------            

                await retry_async(
                   apply_rating_filter,
                    page,
                    rating,
                   action_name="Rating Filter"
                )

                # ==================================
                # GET PRODUCTS
                # ==================================

                selected_products = await retry_async(
                    get_products,
                    page,
                    action_name=f"Get Products - {product}"
                )

                if selected_products:

                    successful_products += 1

                    logger.info(
                        f"Products extracted for {product}"
                    )

                    # ==================================
                    # SEND PRODUCT EMAIL
                    # ==================================

                    send_product_email(
                        selected_products
                    )

                else:

                    failed_products += 1

                    error_message = (
                        f"No products found for {product}"
                    )

                    errors.append(error_message)

                    logger.error(error_message)

            except Exception as e:

                failed_products += 1

                error_message = (
                    f"{product}: {str(e)}"
                )

                errors.append(error_message)

                logger.warning(
                    f"Product processing failed: {e}"
                )

                send_exception_email(
                        exception=e,
                        start_time=start_time,
                        bot_name="Flipkart Automation"
                )

                logger.info(
                    f"Exception email sent for {product}"
                )

                # Continue with next product
                continue

        # ==========================================
        # END TIME
        # ==========================================

        end_time = datetime.now()

        # ==========================================
        # EXECUTION EMAIL
        # ==========================================

        send_execution_email(
            start_time=start_time,
            end_time=end_time,
            total_products=total_products,
            successful_products=successful_products,
            failed_products=failed_products,
            errors=errors
        )

        logger.info(
            "Execution email sent."
        )


        return playwright, browser, context, page

    except Exception as e:

        logger.exception(f"Automation failed: {e}")
        print(f"Automation failed: {e}")

        end_time = datetime.now()

        errors.append(str(e))

        send_exception_email(
        exception=e,
        start_time=start_time
        )

        # Send execution mail even when
        # the entire bot fails.

        send_execution_email(
            start_time=start_time,
            end_time=end_time,
            total_products=0,
            successful_products=0,
            failed_products=1,
            errors=errors
        )

        raise 

    finally:

        # ==========================================
        # CLEANUP
        # ==========================================

        if context:

            try:

                await context.close()

                logger.info(
                    "Browser context closed."
                )

            except Exception as e:

                logger.error(
                    f"Error closing context: {e}"
                )

        if browser:

            try:

                await browser.close()

                logger.info(
                    "Browser closed."
                )

            except Exception as e:

                logger.error(
                    f"Error closing browser: {e}"
                )

        if playwright:

            try:

                await playwright.stop()

                logger.info(
                    "Playwright stopped."
                )

            except Exception as e:

                logger.error(
                    f"Error stopping Playwright: {e}"
                )