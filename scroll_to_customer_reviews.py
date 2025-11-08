# go_to_customer_reviews.py
from playwright.sync_api import sync_playwright
import time

def open_reviews_section():
    url = "https://www.amazon.in/s?k=novels&i=stripbooks&crid=AD02FPL0UXRQ&sprefix=novels%2Cstripbooks%2C392&ref=nb_sb_noss_2"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print("Opening Amazon novels page...")
        page.goto(url, timeout=60000)
        page.wait_for_selector("div.s-main-slot")

        time.sleep(3)

        # Click the link for the specific book
        print("Clicking the 'White Nights' book link...")
        page.click("a:has-text('White Nights – Fyodor Dostoyevsky')")

        # Switch to new tab (Amazon opens product pages in new tab)
        new_page = context.wait_for_event("page")
        new_page.wait_for_load_state()

        # Wait for product title and print
        new_page.wait_for_selector("#productTitle")
        title = new_page.query_selector("#productTitle").inner_text().strip()
        print("\nBook Title:", title)

        # Wait for the Customer Reviews heading and click it
        print("Navigating to Customer Reviews section...")
        new_page.wait_for_selector("h2#averageCustomerReviewsAnchor", timeout=10000)

        # Scroll into view and click
        reviews_heading = new_page.query_selector("h2#averageCustomerReviewsAnchor")
        reviews_heading.scroll_into_view_if_needed()
        time.sleep(1)
        reviews_heading.click()

        print("✅ Opened the Customer Reviews section successfully.")

        time.sleep(3)
        browser.close()

if __name__ == "__main__":
    open_reviews_section()
