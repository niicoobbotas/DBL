import os
import json

# Directory containing conversation files
conversations_dir = "C:\\Users\\nicol\\OneDrive - TU Eindhoven\\Desktop\\Data Challenge\\extracted_conversations"
output_file = "C:\\Users\\nicol\\OneDrive - TU Eindhoven\\Desktop\\Data Challenge\\Programing\\all_non_airline_tweets.json"

# Set of airline user IDs
airline_ids = {
    56377143, 106062176, 18332190, 22536055, 124476322, 26223583,
    2182373406, 38676903, 1542862735, 253340062, 218730857, 45621423, 20626359
}

all_tweets = []

for filename in os.listdir(conversations_dir):
    if filename.endswith('.json'):
        file_path = os.path.join(conversations_dir, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            conversations = json.load(f)
            for conversation in conversations:
                for tweet in conversation:
                    if tweet.get("user", {}).get("id") not in airline_ids:
                        all_tweets.append(tweet)

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_tweets, f, ensure_ascii=False, indent=2)

print(f"Extracted {len(all_tweets)} non-airline tweets to {output_file}")