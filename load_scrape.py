# amazon_novels_scraper.py
from playwright.sync_api import sync_playwright
import time

def scrape_amazon_novels():
    url = "https://www.amazon.in/s?k=novels&i=stripbooks&crid=AD02FPL0UXRQ&sprefix=novels%2Cstripbooks%2C392&ref=nb_sb_noss_2"

    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print("Opening Amazon novels page...")
        page.goto(url, timeout=60000)
        page.wait_for_selector("div.s-main-slot")

        # Wait a bit for all elements to load
        time.sleep(3)

        # Select all book titles
        titles = page.query_selector_all("h2 a span")

        print("\n--- Top Book Titles ---")
        for i, title in enumerate(titles[:10], start=1):  # Limit to top 10
            print(f"{i}. {title.inner_text().strip()}")

        browser.close()

if __name__ == "__main__":
    scrape_amazon_novels()
