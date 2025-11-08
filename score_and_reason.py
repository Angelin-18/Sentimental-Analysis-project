# gemini_sentiment_score_with_reason_updated.py
# Reads Excel file with sentiment info, scores it (-10 to +10),
# adds reasons for each score using Gemini, and saves a new Excel file.

import os
import time
import json
import pandas as pd
import google.generativeai as genai

# -------------------------- CONFIG --------------------------
INPUT_FILE = "reviews_with_sentiment_batched11.xlsx"       # Your Excel input file
OUTPUT_FILE = "reviews_scored_reasoned11.xlsx"              # Output file
BATCH_SIZE = 10                                  # Gemini batch size
DELAY_BETWEEN_BATCHES = 3                        # Seconds between requests
MAX_RETRIES = 2                                  # Retry attempts

# -------------------------- API SETUP --------------------------
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found. Set it using: setx GEMINI_API_KEY 'your_key'")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-flash-latest")

# -------------------------- PROMPT BUILDER --------------------------
def build_prompt(batch_df):
    """
    Builds a single Gemini prompt for a batch of reviews.
    The model will output JSON array of objects:
    [{"score": int, "reason": "..."}, ...]
    """
    text = "\n\n".join([
        f"{i+1}. Review: {row['reviews_translated'] if row['reviews_translated'] != 'no change' else row['review_text']}\n"
        f"Sentiment: {row['Sentiment']}"
        for i, row in batch_df.iterrows()
    ])

    prompt = f"""
You are a sentiment scoring assistant.  
Each review already has a labeled sentiment (Positive, Neutral, or Negative).

Your job:
1. Assign a numeric sentiment score between -10 and +10.
   - Positive sentiment: +4 to +10  
   - Neutral sentiment: -3 to +3  
   - Negative sentiment: -10 to -4  
2. Give a short, clear reason for the score.

Return only a **JSON array** of objects, one for each review, like this:
[
  {{"score": 8, "reason": "Strongly positive tone with enthusiastic wording"}},
  {{"score": -6, "reason": "Critical comments about the book quality"}}
]

Here are the reviews to analyze:
{text}
"""
    return prompt

# -------------------------- PARSER --------------------------
def parse_json_response(response_text):
    """Extracts valid JSON list of dictionaries from Gemini response text."""
    try:
        start = response_text.find("[")
        end = response_text.rfind("]") + 1
        json_str = response_text[start:end]
        return json.loads(json_str)
    except Exception:
        raise ValueError("❌ Could not parse JSON from Gemini response")

# -------------------------- GEMINI CALL --------------------------
def process_batch(batch_df):
    """Send a batch of reviews to Gemini and get scores + reasons."""
    prompt = build_prompt(batch_df)
    attempt = 0
    while attempt <= MAX_RETRIES:
        attempt += 1
        try:
            response = model.generate_content(prompt)
            results = parse_json_response(response.text)
            return results
        except Exception as e:
            print(f"⚠️ Attempt {attempt} failed: {e}")
            if attempt <= MAX_RETRIES:
                time.sleep(5 * attempt)
            else:
                return [{"score": None, "reason": "Error during processing"} for _ in range(len(batch_df))]

# -------------------------- MAIN --------------------------
def main():
    try:
        df = pd.read_excel(INPUT_FILE)
    except FileNotFoundError:
        print(f"❌ File '{INPUT_FILE}' not found.")
        return
    except PermissionError:
        print(f"❌ Close '{INPUT_FILE}' if open and retry.")
        return

    required_cols = {"book_title", "review_text", "reviews_translated", "review_date", "Sentiment"}
    if not required_cols.issubset(df.columns):
        print(f"❌ Input file must contain these columns: {required_cols}")
        return

    scores, reasons = [], []
    print(f"📘 Processing {len(df)} reviews in batches of {BATCH_SIZE}...")

    for start in range(0, len(df), BATCH_SIZE):
        end = min(start + BATCH_SIZE, len(df))
        batch_df = df.iloc[start:end]
        print(f"🔹 Batch {start // BATCH_SIZE + 1}: {start+1}–{end}")
        results = process_batch(batch_df)

        for r in results:
            scores.append(r.get("score"))
            reasons.append(r.get("reason"))
        time.sleep(DELAY_BETWEEN_BATCHES)

    # Add new columns
    df["Sentiment_Score"] = scores
    df["Reason"] = reasons

    # Save to new Excel file
    try:
        df.to_excel(OUTPUT_FILE, index=False, engine="openpyxl")
        print(f"\n✅ Done — Saved as '{OUTPUT_FILE}'")
    except PermissionError:
        print(f"❌ Close '{OUTPUT_FILE}' if it's open and re-run.")
    except Exception as e:
        print(f"⚠️ Unexpected error while saving: {e}")


if __name__ == "__main__":
    main()
