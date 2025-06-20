import os
import json
import psycopg2
import psycopg2.extras
from typing import Dict

# --- CONFIG ---
folder_path = r"C:\\Users\\Admin\\Documents\\subjects\\DBL project\\data DBL\\sprint 2 data"
sql_schema_path = r"C:\\Users\\Admin\\Documents\\subjects\\DBL project\\fixed tables.sql"
BATCH_SIZE = 3000

def get_new_cursor(conn):
    return conn.cursor()

def extract_relevant_info(tweet: Dict) -> Dict:
    urls = tweet.get('entities', {}).get('urls', [])
    cleaned_urls = [{'url': u.get('url'), 'display_url': u.get('display_url')} for u in urls]
    return {
        'created_at': tweet.get('created_at'),
        'id': tweet.get('id'),
        'text': tweet.get('text') or tweet.get('extended_tweet', {}).get('full_text') or "",
        'lang': tweet.get('lang'),
        'retweet_count': tweet.get('retweet_count'),
        'favorite_count': tweet.get('favorite_count'),
        'in_reply_to_status_id': tweet.get('in_reply_to_status_id'),
        'in_reply_to_user_id': tweet.get('in_reply_to_user_id'),
        'in_reply_to_screen_name': tweet.get('in_reply_to_screen_name'),
        'is_quote_status': tweet.get('is_quote_status'),
        'quote_count': tweet.get('quote_count'),
        'reply_count': tweet.get('reply_count'),
        'place': tweet.get('place'),
        'favorited': tweet.get('favorited'),
        'retweeted': tweet.get('retweeted'),
        'user': {
            'id': tweet.get('user', {}).get('id'),
            'screen_name': tweet.get('user', {}).get('screen_name'),
            'name': tweet.get('user', {}).get('name'),
            'followers_count': tweet.get('user', {}).get('followers_count'),
            'friends_count': tweet.get('user', {}).get('friends_count'),
            'favourites_count': tweet.get('user', {}).get('favourites_count'),
            'statuses_count': tweet.get('user', {}).get('statuses_count'),
            'verified': tweet.get('user', {}).get('verified'),
            'location': tweet.get('user', {}).get('location'),
            'time_zone': tweet.get('user', {}).get('time_zone'),
            'created_at': tweet.get('user', {}).get('created_at')
        }
    }

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

    with open(sql_schema_path, "r") as sql_file:
        cur.execute(sql_file.read())
        conn.commit()

    for filename in os.listdir(folder_path):
        if not filename.endswith('.json'):
            continue

        file_path = os.path.join(folder_path, filename)
        print(f"\n📂 Processing file: {filename}")
        successful_inserts = 0
        tweets_batch = []
        users_batch = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not isinstance(data, list):
                    continue

                for item in data:
                    tweets = item if isinstance(item, list) else [item]

                    for tweet in tweets:
                        if not isinstance(tweet, dict):
                            continue
                        try:
                            tweet_info = extract_relevant_info(tweet)
                            user_info = tweet_info['user']

                            users_batch.append((
                                user_info['id'], user_info['screen_name'], user_info['name'],
                                user_info['followers_count'], user_info['friends_count'],
                                user_info['favourites_count'], user_info['statuses_count'],
                                user_info['verified'], user_info['location'],
                                user_info['time_zone'], user_info['created_at']
                            ))

                            tweets_batch.append((
                                tweet_info['id'], user_info['id'], tweet_info['created_at'],
                                tweet_info['text'], tweet_info['lang'], tweet_info['retweet_count'],
                                tweet_info['favorite_count'], tweet_info['in_reply_to_status_id'],
                                tweet_info['in_reply_to_user_id'], tweet_info['in_reply_to_screen_name'],
                                tweet_info['is_quote_status'], tweet_info['quote_count'],
                                tweet_info['reply_count'],
                                tweet_info['place'].get('full_name') if tweet_info['place'] else None,
                                tweet_info['favorited'], tweet_info['retweeted']
                            ))

                            successful_inserts += 1

                            if successful_inserts % BATCH_SIZE == 0:
                                psycopg2.extras.execute_values(cur, """
                                    INSERT INTO users (
                                        user_id, screen_name, name, followers_count, friends_count,
                                        favourites_count, statuses_count, verified, location,
                                        time_zone, created_at
                                    ) VALUES %s
                                    ON CONFLICT (user_id) DO NOTHING
                                """, users_batch)

                                psycopg2.extras.execute_values(cur, """
                                    INSERT INTO tweets (
                                        tweet_id, user_id, created_at, text, lang, retweet_count,
                                        favorite_count, in_reply_to_status_id, in_reply_to_user_id,
                                        in_reply_to_screen_name, is_quote_status, quote_count,
                                        reply_count, place, favorited, retweeted
                                    ) VALUES %s
                                    ON CONFLICT (tweet_id) DO NOTHING
                                """, tweets_batch)

                                conn.commit()
                                print(f" Inserted {successful_inserts} tweets from {filename}")
                                tweets_batch.clear()
                                users_batch.clear()

                        except Exception as e:
                            print(f"❌ Failed to process tweet {tweet.get('id')}: {e}")
                            conn.rollback()
                            cur.close()
                            cur = get_new_cursor(conn)

            # Final commit
            if tweets_batch:
                psycopg2.extras.execute_values(cur, """
                    INSERT INTO users (
                        user_id, screen_name, name, followers_count, friends_count,
                        favourites_count, statuses_count, verified, location,
                        time_zone, created_at
                    ) VALUES %s
                    ON CONFLICT (user_id) DO NOTHING
                """, users_batch)

                psycopg2.extras.execute_values(cur, """
                    INSERT INTO tweets (
                        tweet_id, user_id, created_at, text, lang, retweet_count,
                        favorite_count, in_reply_to_status_id, in_reply_to_user_id,
                        in_reply_to_screen_name, is_quote_status, quote_count,
                        reply_count, place, favorited, retweeted
                    ) VALUES %s
                    ON CONFLICT (tweet_id) DO NOTHING
                """, tweets_batch)

                conn.commit()
                print(f"Final commit succeeded for {filename} (Inserted: {successful_inserts})")

            cur.execute("SELECT COUNT(*) FROM tweets;")
            print(f" Current total tweets in DB: {cur.fetchone()[0]}")

        except Exception as e:
            print(f" Fatal error processing {filename}: {e}")
            conn.rollback()
            cur.close()
            cur = get_new_cursor(conn)

except Exception as e:
    print(f" Could not connect to DB: {e}")

finally:
    try:
        cur.close()
        conn.close()
        print("✅ Done and connection closed.")
    except Exception as e:
        print(f"⚠️ Error closing connection: {e}")
