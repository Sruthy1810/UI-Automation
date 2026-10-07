import re
import logging
from pathlib import Path
from config.config_reader import get_cart_url
from datetime import datetime, time

from modules.excel_reader import normalize_size

logger = logging.getLogger(__name__)
CART_URL = get_cart_url()

async def select_size(page, size):
    size = normalize_size(row.get("Size"))
    exact = re.compile(rf"^\s*{re.escape(size)}\s*$", re.IGNORECASE)

    # ---- Type A: size tiles that are links (numeric sizes like 38, 40, 44) ----
    tile = page.locator("a[href*='swatchAttr=size']").filter(has_text=exact).first
    if await tile.count() > 0:
        await tile.scroll_into_view_if_needed()

        # Sold-out tiles have grey text rgb(112,112,112); available ones are rgb(51,51,51)
        color = await tile.evaluate(
            """el => {
                const t = [...el.querySelectorAll('div')]
                    .find(d => d.children.length === 0 && d.textContent.trim() !== '');
                return t ? getComputedStyle(t).color : '';
            }"""
        )
        if "112, 112, 112" in color:
            raise Exception(f"Size '{size}' is out of stock")

        old_url = page.url
        await tile.click()
        # the link opens the variant page for that size
        try:
            await page.wait_for_url(lambda u: u != old_url, timeout=8000)
        except Exception:
            pass  # already selected / same URL
        await page.wait_for_load_state("domcontentloaded")
        await page.wait_for_timeout(1000)
        logger.info(f"Selected size (link): {size}")
        return

    # ---- Type B: non-link tiles (S, M, XL ... in the popup), case-insensitive heading ----
    heading = ("translate(normalize-space(text()),"
               "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')='select size'")
    xp = (
    "xpath=(//*[" + heading + "]/following::*["
    "translate(normalize-space(text()),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ')"
    f"='{size.upper()}'])[1]"
    )
    btn = page.locator(xp)
    if await btn.count() > 0:
        await btn.scroll_into_view_if_needed()
        await btn.click(force=True)
        await page.wait_for_timeout(800)
        logger.info(f"Selected size: {size}")
        return

    raise Exception(f"Size '{size}' not available for this product")


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




async def add_product_to_cart(context, product_url, size=None):
    """Open the product in its own tab, click Add to cart, close the tab."""
    product_page = await context.new_page()
    
    try:
        
        await product_page.goto(product_url, wait_until="domcontentloaded")
        title = await product_page.title()
        logger.info(f"Opened product: {title}")


                # ---------- SELECT SIZE (if given in Excel) ----------   # NEW
        if size:
            await select_size(product_page, size)
        # -----------------------------------------------------

        kind = await click_add_to_cart(product_page)

        try:
        # Flipkart redirects to the cart after adding
            await product_page.wait_for_function(
                """(kind) => {
                        if (location.href.includes('cart')) return true;
                        if (/go to cart|added to cart/i.test(document.body.textContent)) return true;
                        if (kind === 'icon' && !document.querySelector('#AddToCart_a')) return true;
                        return false;
                    }""",
                    arg=kind,
                    timeout=10000
                )
        except Exception:
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

async def add_items_to_cart(context, items):
    """
    Adds each item to the cart.
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
        size = item.get("size")

        if not url:
            reason = "no product link"
            failed_reasons.append(f"{name}: {reason}")
            results.append({"item": item, "status": "FAILED", "reason": reason, "time": now()})
            continue

        try:
            await add_product_to_cart(context, url, size)
            added_items.append(item)
            results.append({"item": item, "status": "SUCCESS", "reason": "", "time": now()})
        except Exception as e:
            reason = str(e).splitlines()[0][:120]
            failed_reasons.append(f"{name}: {reason}")
            logger.warning(f"Add to cart failed for {name}: {reason}")
            results.append({"item": item, "status": "FAILED", "reason": reason, "time": now()})

    return added_items, failed_reasons, results