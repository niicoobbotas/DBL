import os
import json

#
user_tweets_path = r"C:\Users\nicol\OneDrive - TU Eindhoven\Desktop\Data Challenge\all_non_airline_tweets_with_sentiment.json"
conversations_dir = r"C:\Users\nicol\OneDrive - TU Eindhoven\Desktop\Data Challenge\extracted_conversations"
output_dir = r"C:\Users\nicol\OneDrive - TU Eindhoven\Desktop\Data Challenge\conversations_with_sentiment"
os.makedirs(output_dir, exist_ok=True)


with open(user_tweets_path, "r", encoding="utf-8") as f:
    user_tweets = json.load(f)
user_tweet_lookup = {tweet["id"]: tweet for tweet in user_tweets}

for filename in os.listdir(conversations_dir):
    if filename.endswith('.json'):
        input_path = os.path.join(conversations_dir, filename)
        output_path = os.path.join(output_dir, filename)
        with open(input_path, "r", encoding="utf-8") as f:
            conversations = json.load(f)
        for conversation in conversations:
            for tweet in conversation:
                tweet_id = tweet.get("id")
                if tweet_id in user_tweet_lookup:
                    tweet["sentiment_label"] = user_tweet_lookup[tweet_id].get("sentiment_label")
                    tweet["sentiment_score"] = user_tweet_lookup[tweet_id].get("sentiment_score")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(conversations, f, ensure_ascii=False, indent=2)

print("Done! All conversation files updated with sentiment_label and sentiment_score.")