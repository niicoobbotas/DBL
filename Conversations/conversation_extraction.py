import json
import os
from collections import defaultdict

# Input directory containing JSON files
json_dir_path = "C:\\Users\\nicol\\OneDrive - TU Eindhoven\\Desktop\\Data Challenge\\datacleanedtweets"

# Output directory to store extracted conversations
output_dir_path = "C:\\Users\\nicol\\OneDrive - TU Eindhoven\\Desktop\\Data Challenge\\extracted_conversations"
os.makedirs(output_dir_path, exist_ok=True)

# List of airline IDs
airline_ids = {
    56377143, 106062176, 18332190, 22536055, 124476322, 26223583,
    2182373406, 38676903, 1542862735, 253340062, 218730857, 45621423, 20626359
}

def extract_conversations(tweets):
    """Extract conversations between a user and an airline."""
    conversations = []
    processed_tweets = set()

    # Index tweets by in_reply_to_status_id for quick lookup
    replies_index = defaultdict(list)
    for tweet in tweets:
        if tweet['in_reply_to_status_id'] is not None:
            replies_index[tweet['in_reply_to_status_id']].append(tweet)

    for tweet in tweets:
        # Skip if the tweet is already processed
        if tweet['id'] in processed_tweets:
            continue

        # Start a conversation if the tweet is from a user (not an airline)
        if tweet['user']['id'] not in airline_ids:
            conversation = [tweet]
            processed_tweets.add(tweet['id'])

            # Follow the thread of replies
            current_tweet = tweet
            while True:
                # Find all replies to the current tweet
                replies = replies_index.get(current_tweet['id'], [])

                # Filter replies to include only those from the same user or an airline
                valid_replies = [
                    reply for reply in replies
                    if reply['user']['id'] in airline_ids or reply['user']['id'] == tweet['user']['id']
                ]

                if valid_replies:
                    # Add the first valid reply to the conversation
                    reply = valid_replies[0]
                    conversation.append(reply)
                    processed_tweets.add(reply['id'])
                    current_tweet = reply
                else:
                    # End the conversation if no further valid replies
                    break

            # Ensure the conversation includes at least one tweet before and one tweet after the airline's reply
            airline_replies = [t for t in conversation if t['user']['id'] in airline_ids]
            if airline_replies:
                for airline_reply in airline_replies:
                    airline_index = conversation.index(airline_reply)
                    if (
                        airline_index > 0 and  # At least one tweet before
                        airline_index < len(conversation) - 1 and  # At least one tweet after
                        conversation[airline_index - 1]['user']['id'] == conversation[airline_index + 1]['user']['id'] == tweet['user']['id']
                    ):
                        conversations.append(conversation)
                        break  # Stop checking once the condition is satisfied

    return conversations

# Process all JSON files in the input directory
for filename in os.listdir(json_dir_path):
    if filename.endswith('.json'):
        json_file_path = os.path.join(json_dir_path, filename)
        output_file_path = os.path.join(output_dir_path, f"conversations_{filename}")

        print(f"Processing file: {filename}")

        # Check if the file is empty
        if os.stat(json_file_path).st_size == 0:
            print(f"Skipping empty file: {filename}")
            continue

        with open(json_file_path, 'r', encoding='utf-8') as file:
            try:
                # Load the JSON array of tweets
                tweets = json.load(file)
                print(f"Number of tweets loaded: {len(tweets)}")

                # Extract conversations
                conversations = extract_conversations(tweets)
                print(f"Number of conversations extracted: {len(conversations)}")

                # Save the extracted conversations to a new JSON file
                with open(output_file_path, 'w', encoding='utf-8') as output_file:
                    json.dump(conversations, output_file, ensure_ascii=False, indent=4)

                print(f"Extracted {len(conversations)} conversations from {filename}")

            except json.JSONDecodeError as e:
                print(f"Error decoding JSON in file {filename}: {e}")
                continue
            except Exception as e:
                print(f"Unexpected error processing file {filename}: {e}")
                continue

print("Processing complete.")