# click_book_link.py
from playwright.sync_api import sync_playwright
import time

def click_specific_book():
    url = "https://www.amazon.in/s?k=novels&i=stripbooks&crid=AD02FPL0UXRQ&sprefix=novels%2Cstripbooks%2C392&ref=nb_sb_noss_2"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print("Opening Amazon novels page...")
        page.goto(url, timeout=60000)
        page.wait_for_selector("div.s-main-slot")

        # Wait for content to load
        time.sleep(3)

        # Click the specific link text (partial match for reliability)
        print("Clicking the 'White Nights' book link...")
        link_selector = "a:has-text('White Nights – Fyodor Dostoyevsky')"
        page.click(link_selector)

        # Amazon opens product in new tab — switch to it
        new_page = context.wait_for_event("page")
        new_page.wait_for_load_state()

        # Wait for product title to appear
        new_page.wait_for_selector("#productTitle")

        # Extract and print the book title
        title = new_page.query_selector("#productTitle").inner_text().strip()
        print("\nBook Title:", title)

        browser.close()

if __name__ == "__main__":
    click_specific_book()
