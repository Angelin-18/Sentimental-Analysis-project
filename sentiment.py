# gemini_sentiment_analysis_batched_corrected.py

import os
import time
import pandas as pd
import google.generativeai as genai

# -------------------------- CONFIG --------------------------
INPUT_FILE = "reviews_translated11.xlsx"
OUTPUT_FILE = "reviews_with_sentiment_batched11.xlsx"
BATCH_SIZE = 5           # Number of reviews per batch
DELAY_BETWEEN_BATCHES = 10  # Seconds

# -------------------------- API SETUP --------------------------
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("Set your GEMINI_API_KEY environment variable")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-flash-latest")

# -------------------------- LOAD DATA --------------------------
if INPUT_FILE.endswith(".csv"):
    df = pd.read_csv(INPUT_FILE)
else:
    df = pd.read_excel(INPUT_FILE)

if "review_text" not in df.columns:
    raise ValueError("Input file must contain a 'review_text' column.")

# -------------------------- HELPER FUNCTIONS --------------------------
def build_prompt(batch_reviews):
    """Build a single prompt for a batch of reviews."""
    reviews_text = "\n".join([f"{i+1}. {r}" for i, r in enumerate(batch_reviews)])
    prompt = f"""
You are a sentiment analysis assistant.
For each review below, classify the sentiment as Positive, Neutral, or Negative.
Return only a JSON array of objects like:
[
  {{"sentiment": "Positive"}},
  {{"sentiment": "Neutral"}}
]

Reviews:
{reviews_text}
"""
    return prompt

def parse_response(response_text, batch_len):
    """Extract sentiment list from Gemini response JSON."""
    import json
    try:
        start = response_text.find("[")
        end = response_text.rfind("]") + 1
        json_str = response_text[start:end]
        result = json.loads(json_str)
        # Ensure one sentiment per review
        sentiments = [r.get("sentiment", "Unknown") for r in result]
        if len(sentiments) < batch_len:
            sentiments += ["Unknown"] * (batch_len - len(sentiments))
        return sentiments
    except Exception:
        return ["Unknown"] * batch_len

def analyze_batch(batch_reviews):
    """Send a batch to Gemini and return sentiment results."""
    prompt = build_prompt(batch_reviews)
    try:
        response = model.generate_content(prompt)
        sentiments = parse_response(response.text, len(batch_reviews))
        return sentiments
    except Exception as e:
        print(f"⚠️ Error in batch: {e}")
        return ["Unknown"] * len(batch_reviews)

# -------------------------- MAIN PROCESSING --------------------------
all_sentiments = []

print(f"Processing {len(df)} reviews in batches of {BATCH_SIZE}...")

for start in range(0, len(df), BATCH_SIZE):
    end = min(start + BATCH_SIZE, len(df))
    batch_reviews = df["review_text"].iloc[start:end].tolist()
    print(f"🔹 Batch {start//BATCH_SIZE + 1}: reviews {start+1}-{end}")
    sentiments = analyze_batch(batch_reviews)
    all_sentiments.extend(sentiments)
    time.sleep(DELAY_BETWEEN_BATCHES)

df["Sentiment"] = all_sentiments

# -------------------------- SAVE RESULTS --------------------------
df.to_excel(OUTPUT_FILE, index=False)
print(f"\n✅ Sentiment analysis completed! Saved to '{OUTPUT_FILE}'")
