from playwright.sync_api import sync_playwright
from config.config_reader import get_orangehrm_url
import tkinter as tk


def get_screen_size():

    root = tk.Tk()

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    root.destroy()

    return screen_width, screen_height


def start_browser(playwright):

    screen_width, screen_height = get_screen_size()

    browser = playwright.chromium.launch(
        headless=False,
        args=[
            f"--window-size={screen_width},{screen_height}",
            "--window-position=0,0"
        ]
    )

    url = get_orangehrm_url()

    context = browser.new_context(
        viewport={
            "width": screen_width,
            "height": screen_height
        }
    )

    page = context.new_page()

    page.goto(
        get_orangehrm_url(),
        wait_until="domcontentloaded"
    )

    return browser, context, page