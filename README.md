# Sentimental-Analysis-project
🔍 Learning to perform web scraping using Python Playwright and applying sentiment analysis through Gemini AI to understand customer opinions from real-world data.


# Sentiment Analysis on Amazon Book Reviews using Gemini AI & Playwright

# Project Overview

This project automates the process of web scraping Amazon book reviews using Python Playwright, performs sentiment analysis with Gemini AI, and visualizes review trends over time.
It showcases how a Data Engineer can build an end-to-end data collection → processing → AI analysis → visualization pipeline.

-> Features

🔹 Automated web scraping of Amazon novel reviews using Playwright.

🔹 Data cleaning & structuring with pandas.

🔹 Sentiment classification (Positive / Negative / Neutral) using Gemini AI.

🔹 Scoring the reviews based on the sentiments.

🔹 giving the reason for the specific scores for better understanding of gemini's internal reasoning.

🔹 Trend graph visualization to understand sentiment distribution over time.


📁 Sentiment-Analysis-Amazon-files 

 1. load_scrape.py-Scrapes reviews and book data from Amazon
 2. click_link.py-automating to click the first link
 3. scroll_to_customer_reviews.py - automate scrolling to customer reviews 
 4. extract_reviews_and_dates.py - extract reviews and its particular dates based on the particular reviews
 5. gemini_sentiment_analysis.py - Analyzes sentiments using Gemini AI
 6. reviews_translated.xlsx - Input data file (optional for clean data)
 7. reviews_with_sentiment.xlsx - Output file with sentiments
 8. score_and_reason.py - give score and reason for the particular sentiments
 9. trend_graph.py - Script to generate sentiment trend visualization
 10. README.md - Project documentation

# sentiments

| Review Text                       | Sentiment |
| --------------------------------- | --------- |
| “Loved the story and characters!” | Positive  |
| “Plot was confusing and slow.”    | Negative  |
| “It was okay, not too bad.”       | Neutral   |

# scoring 

the scoring is in the range -10 to 10

   - Positive sentiment: +4 to +10  
   - Neutral sentiment: -3 to +3  
   - Negative sentiment: -10 to -4  

to conclude,this is built as part of my Data Engineering learning journey, this project explores how automation and AI can work together to extract insights from real-world data.

