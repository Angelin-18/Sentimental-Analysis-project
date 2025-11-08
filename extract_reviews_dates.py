# amazon_reviews_scraper_fixed.py
from playwright.sync_api import sync_playwright
import time

def scrape_book_reviews():
    url = "https://www.amazon.in/s?k=novels&i=stripbooks&crid=AD02FPL0UXRQ&sprefix=novels%2Cstripbooks%2C392&ref=nb_sb_noss_2"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print("Opening Amazon novels page...")
        page.goto(url, timeout=60000)
        page.wait_for_selector("div.s-main-slot")
        time.sleep(3)

        # Step 1: Click on the specific book link
        print("Clicking the 'White Nights – Fyodor Dostoyevsky' link...")

        with context.expect_page() as new_page_event:
            try:
                page.click("a:has-text('White Nights – Fyodor Dostoyevsky')")
            except:
                print("⚠️ Could not find that specific book link. Please check the title text.")
                browser.close()
                return

        # Step 2: Handle single-tab vs new-tab case
        try:
            new_page = new_page_event.value
            print("✅ Opened in a new tab.")
        except:
            print("⚠️ No new tab opened; continuing in same page.")
            new_page = page

        # Step 3: Wait for product page to load
        new_page.wait_for_load_state("domcontentloaded")
        new_page.wait_for_selector("#productTitle", timeout=30000)
        title = new_page.query_selector("#productTitle").inner_text().strip()
        print(f"\n📖 Book Title: {title}")

        # Step 4: Scroll to and click Customer Reviews section
        print("Navigating to Customer Reviews section...")
        try:
            new_page.wait_for_selector("h2#averageCustomerReviewsAnchor", timeout=15000)
            heading = new_page.query_selector("h2#averageCustomerReviewsAnchor")
            heading.scroll_into_view_if_needed()
            time.sleep(2)
            heading.click()
            time.sleep(3)
        except:
            print("⚠️ Customer reviews heading not found.")
            browser.close()
            return

        # Step 5: Wait for reviews
        print("Collecting reviews...")
        try:
            new_page.wait_for_selector("div[id^='customer_review']", timeout=30000)
        except:
            print("⚠️ No customer reviews loaded.")
            browser.close()
            return

        # Step 6: Extract review id, date, and text
        print("\n--- Customer Reviews ---\n")
        review_divs = new_page.query_selector_all("div[id^='customer_review']")

        if not review_divs:
            print("No reviews found for this book.")
        else:
            for review in review_divs:
                review_id = review.get_attribute("id")
                text_el = review.query_selector("[data-hook='review-body']")
                date_el = review.query_selector("[data-hook='review-date']")

                review_text = text_el.inner_text().strip().replace("\n", " ") if text_el else "No review text"
                review_date = date_el.inner_text().strip() if date_el else "No date found"

                print(f"🆔 Review ID: {review_id}")
                print(f"📅 Date: {review_date}")
                print(f"💬 Review: {review_text}")
                print("-" * 90)

        browser.close()

if __name__ == "__main__":
    scrape_book_reviews()
