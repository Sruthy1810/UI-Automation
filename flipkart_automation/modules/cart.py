import re
import time
import logging
from pathlib import Path
from datetime import datetime
from modules.email_sender import send_product_email
from config.config_reader import get_cart_url
from modules.excel_reader import parse_sizes

logger = logging.getLogger(__name__)
CART_URL = get_cart_url()


CHIP = 'div[style*="min-width: 52px"]'      # size boxes (S, M, 40, 42 ...)

CONTINUE_STATE_JS = """() => {
  const el = [...document.querySelectorAll('div')].find(
      d => d.children.length === 0 && /^continue$/i.test(d.textContent.trim()));
  if (!el) return 'absent';
  for (let n = el; n && n !== document.body; n = n.parentElement) {
      if (parseFloat(getComputedStyle(n).opacity) < 0.9) return 'disabled';
  }
  return 'enabled';
}"""


async def _continue_state(page):
    """'absent' | 'disabled' | 'enabled'"""
    try:
        return await page.evaluate(CONTINUE_STATE_JS)
    except Exception:
        return "absent"      # e.g. page was navigating


async def _wait_continue_enabled(page, timeout=8000):
    """Waits until Continue is no longer greyed out (opacity 0.5)."""
    waited = 0
    while waited <= timeout:
        state = await _continue_state(page)
        if state == "enabled":
            return "enabled"
        await page.wait_for_timeout(300)
        waited += 300
    return await _continue_state(page)


async def _wait_for_size_chips(page, timeout=10000):
    """Waits for the size boxes to appear on the page."""
    try:
        await page.locator(CHIP).first.wait_for(state="visible", timeout=timeout)
        return True
    except Exception:
        return False




# ---------------------------------------------------------------
# SIZE SELECTION
# ---------------------------------------------------------------
async def _try_size(page, cand):
    """Click one size box, then wait until Continue becomes enabled."""
    chip = page.locator(CHIP).filter(
        has=page.get_by_text(cand, exact=True)
    ).first
    try:
        await chip.wait_for(state="visible", timeout=3000)
    except Exception:
        return "not listed"

    await chip.scroll_into_view_if_needed()
    await chip.click(timeout=5000)
    await page.wait_for_timeout(800)            # let the selection register

    state = await _wait_continue_enabled(page, timeout=5000)
    if state == "disabled":
        return "out of stock or not selectable"
    return "selected"   

async def click_continue(page):
    """Waits for Continue to be enabled, then clicks it."""
    btn = page.get_by_text("Continue", exact=True).first
    await btn.wait_for(state="visible", timeout=8000)

    if await _wait_continue_enabled(page, timeout=8000) == "disabled":
        raise Exception("Continue stayed disabled after selecting size")

    await btn.scroll_into_view_if_needed()
    await page.wait_for_timeout(500)            # short pause before the click
    try:
        await btn.click(timeout=5000)
    except Exception:
        await btn.click(force=True, timeout=5000)
    logger.info("Clicked Continue")


async def select_size(page, size):
    """'40/S' -> tries 40 first, then S. Raises if none can be selected."""
    candidates = parse_sizes(size)
    if not candidates:
        return

    tried = []
    for cand in candidates:
        result = await _try_size(page, cand)
        if result == "selected":
            logger.info(f"Selected size: {cand}")
            return
        tried.append(f"{cand}: {result}")

    raise Exception(f"Size not available ({'; '.join(tried)})")


# ---------------------------------------------------------------
# ADD TO CART
# ---------------------------------------------------------------



async def click_add_to_cart(product_page):
    """Clicks 'Add to cart' (text button) or the cart-plus icon button.
    Returns 'text' or 'icon' so the confirmation check knows what to expect."""

    candidates = [
        # ---- Text versions ----
        ("text", product_page.get_by_role("button", name=re.compile(r"^\s*Add to cart\s*$", re.I))),
        ("text", product_page.locator("xpath=//*[normalize-space(text())='Add to cart']")),
        ("text", product_page.locator(
            "xpath=//div[.//*[normalize-space(text())='Add to cart']][@role='button' or @tabindex or @onclick]")),

        # ---- Icon version (cart with plus sign) ----
        ("icon", product_page.locator("svg:has(clipPath#AddToCart_a)")),
        ("icon", product_page.locator("xpath=//*[name()='svg'][.//*[@id='AddToCart_a']]")),
    ]

    for kind, loc in candidates:
        btn = loc.first
        try:
            await btn.wait_for(state="visible", timeout=3000)
            await btn.scroll_into_view_if_needed()
            await btn.click(timeout=5000)
            logger.info(f"Clicked Add to cart ({kind})")
            return kind
        except Exception:
            continue

    # Last resorts: ignore overlay checks
    text_btn = product_page.get_by_text("Add to cart", exact=True).first
    if await text_btn.count() > 0:
        await text_btn.click(force=True, timeout=5000)
        logger.info("Clicked Add to cart (text, force)")
        return "text"

    icon = product_page.locator("svg:has(clipPath#AddToCart_a)").first
    if await icon.count() > 0:
        await icon.locator("xpath=ancestor::div[3]").click(force=True, timeout=5000)
        logger.info("Clicked Add to cart (icon, force)")
        return "icon"

    raise Exception("Add to cart button not found (neither text nor icon)")

async def check_out_of_stock(page):
    """Checks whether the product shows Notify Me / out-of-stock state."""

    try:
        # Check for Notify Me text
        notify_me = page.get_by_text(
            re.compile(r"^\s*notify\s*me\s*$", re.I)
        )

        count = await notify_me.count()

        for i in range(count):
            element = notify_me.nth(i)

            if await element.is_visible():
                logger.warning("Product is OUT OF STOCK - Notify Me displayed")
                return True

        # Check the specific blue Notify Me container
        notify_container = page.locator(
            'div[style*="linear-gradient(90deg, rgb(35, 129, 252)"]'
        )

        count = await notify_container.count()

        for i in range(count):
            element = notify_container.nth(i)

            if await element.is_visible():
                logger.warning("Product is OUT OF STOCK - Notify Me button found")
                return True

    except Exception as e:
        logger.debug(f"Out of stock check failed: {e}")

    return False

    

async def add_product_to_cart(context, product_url, size=None):
    """Open the product in its own tab, pick size if needed, add to cart, close the tab."""
    product_page = await context.new_page()
    try:
        await product_page.goto(product_url, wait_until="domcontentloaded")
        await product_page.wait_for_timeout(2000)
        title = await product_page.title()
        logger.info(f"Opened product: {title}")


        # --------------------------------------------------
        # CHECK OUT OF STOCK
        # --------------------------------------------------
        #if await check_out_of_stock(product_page):
        #    raise Exception("Product is out of stock")

        if parse_sizes(size):
            # 1) Wait for the size boxes (tap Add to cart first if they are not shown yet)
            if not await _wait_for_size_chips(product_page, timeout=4000):
                await click_add_to_cart(product_page)
                if not await _wait_for_size_chips(product_page, timeout=10000):
                    raise Exception("Size boxes did not appear")

            # 2) Select the size and wait until Continue is enabled
            await select_size(product_page, size)

            # 3) Click Continue (waits for it to be enabled first)
            if await _continue_state(product_page) != "absent":
                await click_continue(product_page)
                kind = "continue"
            else:
                kind = await click_add_to_cart(product_page)
        else:
            kind = await click_add_to_cart(product_page)
            await product_page.wait_for_timeout(1000)
            if "cart" not in product_page.url and \
                    await _continue_state(product_page) != "absent":
                raise Exception("Product needs a size but Size is empty in Excel")

        try:
            await product_page.wait_for_function(
                """(kind) => {
                    if (location.href.includes('cart')) return true;
                    if (/go to cart|added to cart/i.test(document.body.textContent)) return true;
                    if (kind === 'icon' && !document.querySelector('#AddToCart_a')) return true;
                    if (kind === 'continue') {
                        const still = [...document.querySelectorAll('div')].some(
                            d => d.children.length === 0 && /^continue$/i.test(d.textContent.trim()));
                        if (!still) return true;
                    }
                    return false;
                }""",
                arg=kind,
                timeout=10000
            )
        except Exception:
            if not await confirm_added(product_page, kind):
                Path("screenshots").mkdir(exist_ok=True)
                await product_page.screenshot(path=f"screenshots/fail_{int(time.time())}.png")
                raise Exception("Clicked Add to cart but no confirmation appeared")

        logger.info(f"Added to cart: {title}")
        return title
    finally:
        await product_page.close()


async def view_cart(page, screenshot_dir="screenshots"):
    """Open the cart and save a screenshot."""
    await page.goto(CART_URL, wait_until="domcontentloaded")
    await page.wait_for_timeout(3000)

    place_order = page.get_by_text("Place Order", exact=False).first
    if await place_order.is_visible():
        logger.info("Cart loaded with items")
    else:
        logger.warning("Cart looks empty or did not load")

    Path(screenshot_dir).mkdir(exist_ok=True)
    shot = Path(screenshot_dir) / "cart.png"
    await page.screenshot(path=str(shot), full_page=True)
    logger.info(f"Cart screenshot saved: {shot}")
    return shot


async def add_items_to_cart(context, items, size=None, search_term=None):
    """
    Adds each item to the cart and sends one mail per product.
    Returns (added_items, failed_reasons, results)
    """
    added_items = []
    failed_reasons = []
    results = []

    def now():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for item in items:
        name = item.get("name") or item.get("title") or "Unknown product"
        url = item.get("link") or item.get("url")
        item_size = item.get("size") or item.get("Size") or size
        row_num = item.get("Row") or item.get("row")

        if not url:
            reason = "no product link"
            failed_reasons.append(f"{name}: {reason}")
            results.append({"item": item, "row": row_num, "status": "FAILED",
                            "reason": reason, "time": now()})
            send_product_email(item, cart_status="Failed",
                               size=item_size, search_term=search_term)
            continue

        try:
            await add_product_to_cart(context, url, item_size)
            added_items.append(item)
            results.append({"item": item, "row": row_num, "status": "SUCCESS",
                            "reason": "", "time": now()})
            send_product_email(item, cart_status="Success",
                               size=item_size, search_term=search_term)
        except Exception as e:
            lines = str(e).splitlines()
            reason = (lines[0] if lines else type(e).__name__)[:120]
            failed_reasons.append(f"{name}: {reason}")
            logger.warning(f"Add to cart failed for {name}: {reason}")
            results.append({"item": item, "row": row_num, "status": "FAILED",
                            "reason": reason, "time": now()})
            send_product_email(item, cart_status="Failed",
                               size=item_size, search_term=search_term)

    return added_items, failed_reasons, results

CONFIRM_JS = """(kind) => {
    if (location.href.includes('cart')) return true;
    if (/go to cart|added to cart|item added/i.test(document.body.textContent)) return true;
    if (kind === 'icon' && !document.querySelector('#AddToCart_a')) return true;
    if (kind === 'continue') {
        const still = [...document.querySelectorAll('div')].some(
            d => d.children.length === 0 && /^continue$/i.test(d.textContent.trim()));
        if (!still) return true;
    }
    return false;
}"""


async def confirm_added(page, kind, timeout=10000):
    """Polls until the add is confirmed."""

    waited = 0

    while waited <= timeout:

        # Check whether page is already closed
        try:
            if page.is_closed():
                logger.warning("Product page was closed during confirmation")
                return False
        except Exception:
            return False

        # Redirect to cart = success
        try:
            if "cart" in page.url.lower():
                return True
        except Exception:
            return False

        try:
            if await page.evaluate(CONFIRM_JS, kind):
                return True

        except Exception:
            # Page may be navigating
            pass

        # IMPORTANT:
        # Don't call wait_for_timeout if page is already closed
        try:
            if page.is_closed():
                return False

            await page.wait_for_timeout(500)

        except Exception:
            return False

        waited += 500

    return False