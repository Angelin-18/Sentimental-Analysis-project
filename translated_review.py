# translate_reviews_gemini.py
# Reads an Excel file with a "review_text" column,
# translates non-English reviews to English using Gemini,
# marks English reviews as "no change",
# and saves the final Excel file in correct column order.

import os
import time
import json
import pandas as pd
import google.generativeai as genai

# ----------------------------- CONFIG -----------------------------
INPUT_FILE = "amazon_book_reviews.xlsx"        # <-- your input Excel file
OUTPUT_FILE = "reviews_translated11.xlsx"
BATCH_SIZE = 8
DELAY_BETWEEN_BATCHES = 3
MAX_RETRIES = 2

# ----------------------------- API SETUP -----------------------------
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found. Set it with: setx GEMINI_API_KEY 'your_key'")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-flash-latest")

# ----------------------------- FUNCTIONS -----------------------------
def build_prompt(batch_reviews):
    """Build translation prompt for Gemini."""
    joined = "\n\n".join([f"{i+1}. {r}" for i, r in enumerate(batch_reviews)])
    prompt = f"""
You are a translation assistant.

For each review below:
- If it's already in English, return exactly "no change".
- If it's in another language, return its English translation.

Return only a JSON array of strings, each corresponding to the same order as input reviews.

Example:
["no change", "This book was wonderful", "no change"]

Reviews:
{joined}
"""
    return prompt


def parse_json_array_from_text(text):
    """Extract JSON array safely from Gemini output."""
    start = text.find('[')
    end = text.rfind(']') + 1
    if start == -1 or end == 0:
        raise ValueError("No JSON array found in response")
    json_str = text[start:end]
    return json.loads(json_str)


def translate_batch(batch_reviews):
    """Translate a batch of reviews using Gemini."""
    attempt = 0
    while attempt <= MAX_RETRIES:
        attempt += 1
        try:
            prompt = build_prompt(batch_reviews)
            response = model.generate_content(prompt)
            raw = response.text.strip()
            return parse_json_array_from_text(raw)
        except Exception as e:
            print(f"⚠️ Attempt {attempt} failed: {e}")
            if attempt <= MAX_RETRIES:
                time.sleep(5 * attempt)
            else:
                return ["error" for _ in batch_reviews]


# ----------------------------- MAIN -----------------------------
def main():
    try:
        df = pd.read_excel(INPUT_FILE)
    except FileNotFoundError:
        print(f"❌ File '{INPUT_FILE}' not found.")
        return
    except PermissionError:
        print(f"❌ Close '{INPUT_FILE}' if open and retry.")
        return

    if "review_text" not in df.columns:
        print("❌ Excel file must contain a 'review_text' column.")
        return

    df["review_text"] = df["review_text"].fillna("").astype(str)
    reviews = df["review_text"].tolist()
    translated = []

    print(f"🌍 Translating {len(reviews)} reviews in batches of {BATCH_SIZE}...")

    for start in range(0, len(reviews), BATCH_SIZE):
        end = min(start + BATCH_SIZE, len(reviews))
        batch = reviews[start:end]
        print(f"🔹 Batch {start // BATCH_SIZE + 1}: {start+1}–{end}")
        results = translate_batch(batch)
        translated.extend(results)
        time.sleep(DELAY_BETWEEN_BATCHES)

    # Insert translated column next to review_text
    df.insert(df.columns.get_loc("review_text") + 1, "reviews_translated", translated)

    # Ensure correct column naming and order
    df.rename(columns={
        "Book_Title": "book_title",
        "Review_Date": "review_date"
    }, inplace=True)

    expected_order = ["book_title", "review_text", "reviews_translated", "review_date"]
    df = df[[col for col in expected_order if col in df.columns]]

    try:
        df.to_excel(OUTPUT_FILE, index=False, engine="openpyxl")
        print(f"\n✅ Done — saved translated file as '{OUTPUT_FILE}' with proper column order.")
    except PermissionError:
        print(f"❌ Close '{OUTPUT_FILE}' if it's open and re-run.")
    except Exception as e:
        print(f"⚠️ Unexpected error while saving: {e}")


if __name__ == "__main__":
    main()


