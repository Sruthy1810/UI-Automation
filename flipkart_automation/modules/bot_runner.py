from browser.browser_manager import start_browser
from config.config_reader import (get_flipkart_url,get_email,get_login_type,get_phonenumber,get_product_file)
from utils.logger import logger
from modules.login import open_flipkart
from modules.excel_reader import read_products,update_found_status,update_cart_status,is_already_found
import asyncio
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
from utils.screenshot import take_failure_screenshot
from utils.archive import archive_old_files
from modules.cart import add_product_to_cart, view_cart, add_items_to_cart
from modules.retry import retry_async



async def close_browser(playwright, browser, context, page):
    """Close everything quickly. A hung step is skipped after 5 seconds."""

    async def safe_close(obj, label):
        if not obj:
            return
        try:
            await asyncio.wait_for(obj.close(), timeout=5)
        except Exception as e:
            logger.warning(f"{label} close skipped: {e}")

    await safe_close(page, "Page")
    await safe_close(context, "Context")
    await safe_close(browser, "Browser")

    # Stopping Playwright also kills any browser process that is still hanging
    if playwright:
        try:
            await asyncio.wait_for(playwright.stop(), timeout=5)
        except Exception as e:
            logger.warning(f"Playwright stop skipped: {e}")

    logger.info("Browser closed.")

def is_already_success(product_data):
    status = str(product_data.get("Status") or "").strip().lower()
    return status == "success"   

async def run_bot():

    logger.info("BOT RUNNER STARTED")
    print("BOT RUNNER STARTED")

    start_time = datetime.now()

    archive_old_files(keep_logs=2, keep_screenshots=2)

    successful_products = 0
    failed_products = 0
    skipped_products = 0 
    total_products = 0
    cart_items = []          
    added_to_cart = 0 
    errors = []

    excel_products = []      
    done_rows = set()

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
        # TRIGGER EMAIL and Read Excel data
        # ==========================================



        all_products = read_products()

        excel_products = [p for p in all_products if not is_already_success(p)]
        skipped_products = len(all_products) - len(excel_products)
        total_products = len(excel_products)

        logger.info(
            f"Products in Excel: {len(all_products)} | "
            f"Already Success (skipped): {skipped_products} | "
            f"To process: {total_products}"
        )

        if total_products == 0:
            logger.info("All products are already marked Success. Nothing to do.")
            print("All products are already marked Success. Nothing to do.")
            return playwright, browser, context, page

        send_trigger_email(total_products)
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
        # Process Products
        # --------------------------------   

        for product_data in excel_products:


            if is_already_success(product_data):
                skipped_products += 1
                logger.info(
                    f"Skipping '{product_data['Product']}' - Status already Success"
                )
                continue

            try:

                product = product_data["Product"]
                price = product_data["Price"]
                rating = product_data["Customer Ratings"]
                size = product_data.get("Size")

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

                    items = [
                        {**sp, "size": size, "Row": product_data["Row"]}
                        for sp in selected_products
                    ]

                    # ----- Add the selected products to cart -----
                    added_items, failed_reasons, results = await add_items_to_cart(
                        context, selected_products, size=size, search_term=product
                    )

                    total_selected = len(items)
                    total_added = len(added_items)

                    for r in results:                      # <-- "results" used here
                        send_product_email(
                            r["item"],
                            cart_status="Success" if r["status"] == "SUCCESS" else "Failed",
                            remarks=r["reason"] or "Added to cart",
                            size=size,
                            search_term=product,
                        )

                    if total_added > 0:
                        successful_products += 1
                        send_product_email(added_items)

                        status = "Success"
                        remarks = f"{total_added} of {total_selected} products added to cart"
                        if failed_reasons:
                            remarks += " | Failed: " + "; ".join(failed_reasons)
                    else:
                        failed_products += 1
                        status = "Failed"
                        remarks = "Products found but none could be added to cart"
                        if failed_reasons:
                            remarks += " | " + "; ".join(failed_reasons)
                        errors.append(f"{product}: {remarks}")

                    # Found first (it resets row colour), then the cart status
                    update_found_status(product, "Success", name=product_data["Name"])
                    update_cart_status( product, status, remarks,
                                       name=product_data["Name"], row_num=product_data["Row"])

                else:
                    failed_products += 1
                    error_message = f"No products found for {product}"
                    errors.append(error_message)
                    logger.error(error_message)

                    update_found_status(product, "Failed", name=product_data["Name"])
                    update_cart_status(product, "Failed",
                                       "No products found after applying filters",
                                       name=product_data["Name"], row_num=product_data["Row"])

            except Exception as e:

                # Fatal: browser/page/context is gone, no point continuing
                fatal_markers = (
                    "has been closed",
                    "Target closed",
                    "Browser closed",
                    "Connection closed",
                )
                if any(m.lower() in str(e).lower() for m in fatal_markers):
                    logger.error(f"Browser closed, aborting run: {e}")
                    raise

                screenshot_path = await take_failure_screenshot(
                    page,
                    f"{product}_error"
                )               

                failed_products += 1
                error_message = f"{product}: {str(e)}"
                errors.append(error_message)

                update_found_status(
                    product,
                    "Failed",
                    name=product_data["Name"]
                )

                logger.warning(f"Product processing failed: {e}")

                send_exception_email(
                    e,
                    start_time=start_time,
                    bot_name="Flipkart Automation",
                    screenshot_path=screenshot_path
                )

                logger.info(f"Exception email sent for {product}")
                continue



        try:
            for item in cart_items:
                url = item.get("link") or item.get("url")   # adjust to your key name
                if not url:
                    continue
                try:
                    await retry_async(
                        add_product_to_cart,
                        context,
                        url,
                        action_name="Add to Cart"
                    )
                    added_to_cart += 1
                except Exception as e:
                    errors.append(f"Add to cart failed: {e}")
                    logger.warning(f"Add to cart failed for {url}: {e}")

            await view_cart(page)
            logger.info(f"Cart step done. Added {added_to_cart} item(s).")

        except Exception as e:
            errors.append(f"Cart step failed: {e}")
            logger.exception(f"Cart step failed: {e}")


        logger.info(
        f"Run summary - Success: {successful_products}, "
        f"Failed: {failed_products}, Skipped: {skipped_products}"
)
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

        screenshot_path = None
        if page:
            screenshot_path = await take_failure_screenshot(page, "bot_failed")

        # ---- Mark every unfinished row as Failed in Excel ----
        reason = f"{type(e).__name__}: {str(e).splitlines()[0] if str(e) else ''}"[:250]
        for p in excel_products:
            if p["Row"] in done_rows:
                continue
            update_cart_status(p["Product"], "Failed", reason,
                               name=p["Name"], row_num=p["Row"])
        
        send_exception_email(
            exception=e,
            start_time=start_time,
            bot_name="Flipkart Automation",
            screenshot_path=screenshot_path
        )

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

        await close_browser(playwright, browser, context, page)

