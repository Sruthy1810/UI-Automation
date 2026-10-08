from playwright.async_api import TimeoutError
from utils.logger import logger
from utils.screenshot import take_failure_screenshot
import re
from config.config_reader import get_max_products

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

async def get_products(page, max_products=None):

    logger.info("Getting products...")

    products = []

    try:
        # Wait for product cards to appear
        await page.wait_for_selector("div[data-id]", timeout=10000)

        product_cards = page.locator("div[data-id]")
        total = await product_cards.count()
        logger.info(f"Product cards found: {total}")

        ignore_lines = {"add to compare", "sponsored", "ad", "bestseller", "assured"}

        def clean(text):
            return re.sub(r"\s+", " ", text).strip() if text else ""

        max_products = max_products or get_max_products()

        for i in range(min(total, max_products)):
            card = product_cards.nth(i)

            try:
                card_text = await card.inner_text()
                lines = [clean(l) for l in card_text.split("\n") if clean(l)]

                # -----------------------------
                # Product Name
                # -----------------------------
                name = ""

                # 1) title attribute on any element inside the card
                titled = card.locator("[title]")
                for k in range(await titled.count()):
                    t = clean(await titled.nth(k).get_attribute("title"))
                    if t and len(t) > 5:
                        name = t
                        break

                # 2) image alt text
                if not name:
                    img_alt = card.locator("img").first
                    if await img_alt.count() > 0:
                        alt = clean(await img_alt.get_attribute("alt"))
                        if alt and len(alt) > 5:
                            name = alt

                # 3) first meaningful text line
                if not name:
                    for line in lines:
                        if (
                            line.lower() not in ignore_lines
                            and not re.fullmatch(r"[\d.,₹%\s]+", line)
                        ):
                            name = line
                            break

                name = name or "N/A"

                # -----------------------------
                # Price (current) and MRP
                # -----------------------------
                amounts = re.findall(r"₹\s?([\d,]+)", card_text)
                price = f"₹{amounts[0]}" if amounts else "N/A"
                mrp = f"₹{amounts[1]}" if len(amounts) > 1 else ""

                # -----------------------------
                # Rating
                # -----------------------------
                rating = "N/A"

                # 1) Rating followed by the ratings count, e.g. "4.618,521 Ratings"
                #    or "4.6 18,521 Ratings". The lookahead stops the regex from
                #    swallowing the first digit of the count.
                m = re.search(
                    r"(?<![\d.])([1-5]\.\d)(?=\s*[\d,]+\s*Ratings?)",
                    card_text
                )
                if m:
                    rating = m.group(1)

                # 2) Rating on its own line, e.g. "4.6" or "4.6 ★"
                if rating == "N/A":
                    for line in lines:
                        m = re.fullmatch(r"([1-5](?:\.\d)?)\s*★?", line)
                        if m:
                            rating = m.group(1)
                            break

                # 3) Rating shown with a count in brackets, e.g. "4.3 (1,234)"
                if rating == "N/A":
                    m = re.search(
                        r"(?<![\d.₹,])([1-5]\.\d)\s*\(\s*[\d,.]+[kK]?\s*\)",
                        card_text
                    )
                    if m:
                        rating = m.group(1)

                # 4) Last resort: any small element whose whole text is a rating
                if rating == "N/A":
                    rating_el = card.locator("div, span").filter(
                        has_text=re.compile(r"^\s*[1-5](\.\d)?\s*$")
                    )
                    if await rating_el.count() > 0:
                        rating = clean(await rating_el.first.inner_text())

                # -----------------------------
                # Product URL
                # -----------------------------
                product_url = ""

                link = card.locator("a[href*='/p/']").first
                if await link.count() == 0:
                    link = card.locator("a").first

                if await link.count() > 0:
                    href = await link.get_attribute("href")
                    if href:
                        product_url = (
                            "https://www.flipkart.com" + href
                            if href.startswith("/")
                            else href
                        )

                # -----------------------------
                # Product Image
                # -----------------------------
                image_url = ""

                img = card.locator("img").first
                if await img.count() > 0:
                    image_url = (
                        await img.get_attribute("src")
                        or await img.get_attribute("data-src")
                        or ""
                    )

                # -----------------------------
                # Store Product
                # -----------------------------
                product = {
                    "name": name,
                    "price": price,
                    "mrp": mrp,
                    "rating": rating,
                    "url": product_url,
                    "image": image_url,
                }
                products.append(product)

                logger.info(f"\nProduct {i + 1}")
                logger.info(f"Name   : {name}")
                logger.info(f"Price  : {price}")
                logger.info(f"MRP    : {mrp}")
                logger.info(f"Rating : {rating}")
                logger.info(f"URL    : {product_url}")
                logger.info(f"Image  : {image_url}")

            except Exception as e:
                logger.error(f"Error extracting product {i + 1}: {e}")

        logger.info(f"\nTotal products selected: {len(products)}")
        return products

    except Exception as e:
        logger.error(f"Error getting products: {e}")
        return []
    
