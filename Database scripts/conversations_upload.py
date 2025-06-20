import os
import json
import psycopg2
import psycopg2.extras

# --- CONFIG ---
folder_path = r"C:\Users\Admin\Documents\subjects\DBL project\data DBL\conversationsw_sentiment\conversations_with_sentiment"
BATCH_SIZE = 3000


def get_new_cursor(conn):
    return conn.cursor()

def process_conversations(conversations):
    insert_data = []

    AIRLINE_USER_IDS = {
        56377143: "KLM",
        106062176: "AirFrance",
        18332190: "British_Airways",
        22536055: "AmericanAir",
        124476322: "Lufthansa",
        26223583: "AirBerlin",
        2182373406: "AirBerlin assist",
        38676903: "easyJet",
        1542862735: "Ryanair",
        253340062: "SingaporeAir",
        218730857: "Qantas",
        45621423: "EtihadAirways",
        20626359: "VirginAtlantic"
    }

    for conversation in conversations:
        if not conversation or not isinstance(conversation, list):
            continue

        conv_id = conversation[0].get("id")
        conv_len = len(conversation)

        airline = None
        for tweet in conversation:
            uid = tweet.get("user", {}).get("id")
            if uid in AIRLINE_USER_IDS:
                airline = AIRLINE_USER_IDS[uid]
                break

        # Get all non-airline tweets (user side of the conversation)
        user_tweets = [
            t for t in conversation if t.get("user", {}).get("id") not in AIRLINE_USER_IDS
        ]

        # Get sentiment of first and last user tweets
        sentiment_start = sentiment_end = None
        sentiment_start_score = sentiment_end_score = None

        if user_tweets:
            first_tweet = user_tweets[0]
            last_tweet = user_tweets[-1]
            sentiment_start = first_tweet.get("sentiment_label")
            sentiment_start_score = first_tweet.get("sentiment_score")
            sentiment_end = last_tweet.get("sentiment_label")
            sentiment_end_score = last_tweet.get("sentiment_score")

        for tweet in conversation:
            tweet_id = tweet.get("id")
            user_id = tweet.get("user", {}).get("id")

            if tweet_id and user_id and conv_id:
                insert_data.append((
                    conv_id,
                    user_id,
                    tweet_id,
                    conv_len,
                    sentiment_start,
                    sentiment_start_score,
                    sentiment_end,
                    sentiment_end_score,
                    airline
                ))

    return insert_data



try:
    conn = psycopg2.connect(
        host="dbl.cjiyqqck0poz.eu-west-1.rds.amazonaws.com",
        port=5432,
        dbname="DBL",
        user="postgres",
        password="DblCork2025",
        sslmode="require"
    )
    conn.autocommit = False
    cur = get_new_cursor(conn)

    total_inserted = 0
    batch = []

    print(f" Scanning folder: {folder_path}")
    for filename in os.listdir(folder_path):
        if not filename.endswith('.json'):
            continue

        file_path = os.path.join(folder_path, filename)
        print(f"\nS Processing: {filename}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    new_rows = process_conversations(data)
                    batch.extend(new_rows)
                    print(f"➕ Prepared {len(new_rows)} rows from {filename}")

                    while len(batch) >= BATCH_SIZE:
                        sub_batch = batch[:BATCH_SIZE]
                        psycopg2.extras.execute_values(cur, """
                            INSERT INTO conversations (
                                conversation_id, user_id, tweet_id,
                                conversation_length, sentiment_start, sentiment_start_score, sentiment_end, sentiment_end_score, airline
                            ) VALUES %s
                            ON CONFLICT (conversation_id, tweet_id) DO NOTHING
                        """, sub_batch)
                        conn.commit()
                        total_inserted += len(sub_batch)
                        print(f"✅ Inserted {total_inserted} rows")
                        batch = batch[BATCH_SIZE:]

        except Exception as e:
            print(f" Error in {filename}: {e}")
            conn.rollback()
            cur.close()
            cur = get_new_cursor(conn)

    if batch:
        psycopg2.extras.execute_values(cur, """
            INSERT INTO conversations (
                conversation_id, user_id, tweet_id,
                conversation_length, sentiment_start, sentiment_start_score, sentiment_end, sentiment_end_score, airline
            ) VALUES %s
            ON CONFLICT (conversation_id, tweet_id) DO NOTHING
        """, batch)
        conn.commit()
        total_inserted += len(batch)
        print(f" Final commit — total inserted: {total_inserted}")

except Exception as e:
    print(f" Database connection or execution failed: {e}")
    if conn:
        conn.rollback()

finally:
    try:
        cur.close()
        conn.close()
        print(" Connection closed.")
    except Exception as e:
        print(f" Error closing DB: {e}")
