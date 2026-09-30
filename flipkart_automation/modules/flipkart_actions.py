from playwright.async_api import TimeoutError
from utils.logger import logger
from utils.screenshot import take_failure_screenshot

async def search_product(page, product):

    logger.info(f"Searching product: {product}")

    # --------------------------------
    # Search box
    # --------------------------------

    try:

        search_box = page.locator(
            'input[name="q"]:not([readonly])'
        )

        await search_box.wait_for(
            state="visible",
            timeout=10000
        )

        await search_box.fill(product)
        await page.wait_for_timeout(3000)

        logger.info(f"Product entered: {product}")

        # --------------------------------
        # Search button
        # --------------------------------

        search_button = page.locator(
           'button[type="submit"]'
        )

        await search_button.wait_for(
            state="visible",
            timeout=10000
        )

        await search_button.click()

        logger.info(f"Search clicked: {product}")

        await page.wait_for_timeout(3000)

        # --------------------------------
        # Wait for search results
        # --------------------------------

        await page.wait_for_load_state(
            "domcontentloaded"
        )

        logger.info(
            f"Search completed successfully: {product}"
        )

    except Exception as e:
        logger.error("Search failed")

        screenshot = await take_failure_screenshot(
        page,
        product
        )

        logger.info(
            f"Failure screenshot: {screenshot}"
        )
        
        
        raise

    # --------------------------------
    #   price_filter
    # --------------------------------

async def apply_price_filter(page, price):

    logger.info(f"Applying price filter: {price}")

    try:
                # Check whether Price filter section exists
        price_section = page.locator(
            "section.XC54e7"
        ).filter(
            has_text="Price"
        )

        await price_section.wait_for(
            state="visible",
            timeout=5000
        )

        logger.info("Price filter found.")

        # Get all dropdowns inside Price section
        price_dropdowns = price_section.locator(
            "select.hbnjE2"
        )

        count = await price_dropdowns.count()

        logger.info(f"Price dropdowns found: {count}")

        if count < 2:
            logger.warning("Price dropdowns not found.")
            return

        # --------------------------------
        # Maximum Price
        # --------------------------------

        await price_dropdowns.nth(1).select_option(
            value=str(price)
        )

        logger.info(f"Maximum price selected: {price}")

    except TimeoutError:
        logger.error("Price filter not found.")

    except Exception as e:
        logger.error(f"Price filter error: {e}")




    # --------------------------------
    #   rating_filter
    # --------------------------------
async def apply_rating_filter(page, rating):

    logger.info(f"Applying rating filter: {rating}")

    try:
        # Check whether Customer Ratings section exists
        rating_section = page.locator(
            "section.KNnSWQ"
        ).filter(
            has_text="Customer Ratings"
        ).first

        await rating_section.wait_for(
            state="visible",
            timeout=10000
        )

        logger.info("Customer Ratings filter found.")

        # --------------------------------
        # Convert Excel value
        # --------------------------------

        rating_value = int(float(rating))
        rating_text = f"{rating_value}★ & above"

        logger.info(
            f"Looking for rating option: {rating_text}"
        )

        # --------------------------------
        # Find rating option
        # --------------------------------

        
        rating_option = rating_section.locator(
            f'div[title="{rating_text}"]'
        )

        # --------------------------------
        # Check if rating option is visible
        # --------------------------------

        option_visible = False

        try:

            await rating_option.wait_for(
                state="visible",
                timeout=2000
            )

            option_visible = True

            logger.info(
                "Rating options are already visible."
            )

        except TimeoutError:

            logger.info(
                "Rating options are collapsed. "
                "Clicking Customer Ratings."
            )

        # --------------------------------
        # Expand Customer Ratings
        # --------------------------------

        if not option_visible:

            customer_rating_text = rating_section.get_by_text(
                "Customer Ratings",
                exact=True
            ).first

            await customer_rating_text.click()

            logger.info(
                "Customer Ratings section clicked."
            )

            # Wait until rating option appears
            await rating_option.wait_for(
                state="visible",
                timeout=10000
            )

            logger.info(
                "Rating options are now visible."
            )

        # --------------------------------
        # Find checkbox
        # --------------------------------

        checkbox = rating_option.locator(
            'input[type="checkbox"]'
        )

        await checkbox.wait_for(
            state="attached",
            timeout=10000
        )

        logger.info(
            f"Rating checkbox found: {rating_text}"
        )

        # --------------------------------
        # Check current state
        # --------------------------------

        is_checked = await checkbox.is_checked()

        logger.info(
            f"Current checkbox state: {is_checked}"
        )

        # --------------------------------
        # Click only if not checked
        # --------------------------------

        if not is_checked:

            await rating_option.get_by_text(
                rating_text,
                exact=True
            ).click()

            logger.info(
                f"Rating option clicked: {rating_text}"
            )

        else:

            logger.info(
                f"Rating already selected: {rating_text}"
            )

        # --------------------------------
        # Verify checkbox
        # --------------------------------

        await page.wait_for_timeout(1000)

        is_checked = await checkbox.is_checked()

        if is_checked:

            logger.info(
                f"Rating filter applied successfully: "
                f"{rating_text}"
            )

        else:

            logger.warning(
                f"Rating checkbox is not checked: "
                f"{rating_text}"
            )

    except TimeoutError:

        logger.error(
            "Customer Ratings section, "
            "rating option, or checkbox not found."
        )

        raise

    except ValueError:

        logger.error(
            f"Invalid rating value from Excel: {rating}"
        )

        raise

    except Exception as e:

        logger.error(
            f"Rating filter error: {e}"
        )

        raise


    # --------------------------------
    #   Get Products
    # --------------------------------

async def get_products(page):

    logger.info("Getting products...")

    products = []

    try:
        # Wait for product cards to appear
        await page.wait_for_selector(
            "div[data-id]",
            timeout=10000
        )

        # Get product cards
        product_cards = page.locator("div[data-id]")

        count = await product_cards.count()

        print(f"Product cards found: {count}")

        # Maximum 3 products
        max_products = min(count, 3)

        for i in range(max_products):

            card = product_cards.nth(i)

            try:
                # -----------------------------
                # Product Name
                # -----------------------------
                name = ""

                name_locators = [
                    "div.KzDlHZ",
                    "a.wjcEIp",
                    "div._4rR01T",
                    "a[title]"
                ]

                for selector in name_locators:

                    locator = card.locator(selector)

                    if await locator.count() > 0:
                        name = await locator.first.inner_text()
                        name = name.strip()

                        if name:
                            break

                # -----------------------------
                # Price
                # -----------------------------
                price = ""

                price_locator = card.locator(
                    "div.Nx9bqj",
                    "hZ3P6w DeU9vF"
                )

                if await price_locator.count() > 0:
                    price = await price_locator.first.inner_text()
                    price = price.strip()

                # -----------------------------
                # Rating
                # -----------------------------
                rating = ""

                rating_locator = card.locator(
                    "div.XQDdHH",
                    "MKiFS6"
                )

                if await rating_locator.count() > 0:
                    rating = await rating_locator.first.inner_text()
                    rating = rating.strip()

                # -----------------------------
                # Product URL
                # -----------------------------
                product_url = ""

                link_locator = card.locator("a").first

                if await link_locator.count() > 0:

                    href = await link_locator.get_attribute("href")

                    if href:

                        if href.startswith("/"):
                            product_url = "https://www.flipkart.com" + href
                        else:
                            product_url = href

                # -----------------------------
                # Product Image
                # -----------------------------
                image_url = ""

                image_locator = card.locator("img").first

                if await image_locator.count() > 0:

                    image_url = await image_locator.get_attribute("src")

                    # Sometimes Flipkart uses lazy loading
                    if not image_url:
                        image_url = await image_locator.get_attribute(
                            "data-src"
                        )

                # -----------------------------
                # Store Product
                # -----------------------------
                product = {
                    "name": name,
                    "price":price,
                    "rating": rating,
                    "url": product_url,
                    "image": image_url
                }

                products.append(product)

                logger.info(f"\nProduct {i + 1}")
                logger.info(f"Name   : {name}")
                logger.info(f"Price  : {price}")
                logger.info(f"Rating : {rating}")
                logger.info(f"URL    : {product_url}")
                logger.info(f"Image  : {image_url}")

            except Exception as e:

                logger.error(
                    f"Error extracting product {i + 1}: {e}"
                )

        logger.info(f"\nTotal products selected: {len(products)}")

        return products

    except Exception as e:

        logger.error(f"Error getting products: {e}")

        return []
    
