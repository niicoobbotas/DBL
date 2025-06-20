import os
import json
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from tqdm import tqdm

model_name = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
classifier = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

input_path = r"C:\\Users\\nicol\\OneDrive - TU Eindhoven\\Desktop\\Data Challenge\\all_non_airline_tweets.json"
output_folder = r"C:\\Users\\nicol\\OneDrive - TU Eindhoven\\Desktop\\Data Challenge"
output_filename = "all_non_airline_tweets_with_sentiment.json"
os.makedirs(output_folder, exist_ok=True)
output_path = os.path.join(output_folder, output_filename)

with open(input_path, "r", encoding="utf-8") as f:
    tweets = json.load(f)

for tweet in tqdm(tweets, desc="Analyzing tweets"):
    text = tweet.get("text", "")
    if not text.strip():
        tweet["sentiment_label"] = None
        tweet["sentiment_score"] = None
        continue
    try:
        result = classifier(text)[0]
        tweet["sentiment_label"] = result["label"]
        tweet["sentiment_score"] = round(result["score"], 4)
    except Exception:
        tweet["sentiment_label"] = "ERROR"
        tweet["sentiment_score"] = 0.0

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(tweets, f, indent=2, ensure_ascii=False)

print(f"✅ Enriched file saved to: {output_path}")