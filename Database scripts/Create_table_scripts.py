#ALL DONE IN PGADMIN 4 - WILL NOT WORK IN PYTHON - SCRIPTS OBTAINED FROM "SCRIPTS" - "CREATE SCRIPT"


#Tweets Table 
-- Table: public.tweets

-- DROP TABLE IF EXISTS public.tweets;

CREATE TABLE IF NOT EXISTS public.tweets
(
    tweet_id bigint NOT NULL,
    user_id bigint,
    created_at text COLLATE pg_catalog."default",
    text text COLLATE pg_catalog."default",
    lang text COLLATE pg_catalog."default",
    retweet_count integer,
    favorite_count integer,
    in_reply_to_status_id bigint,
    in_reply_to_user_id bigint,
    in_reply_to_screen_name text COLLATE pg_catalog."default",
    is_quote_status boolean,
    quote_count integer,
    reply_count integer,
    place text COLLATE pg_catalog."default",
    favorited boolean,
    retweeted boolean,
    CONSTRAINT tweets_pkey PRIMARY KEY (tweet_id),
    CONSTRAINT tweets_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES public.users (user_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.tweets
    OWNER to postgres;

#User's table
-- Table: public.users

-- DROP TABLE IF EXISTS public.users;

CREATE TABLE IF NOT EXISTS public.users
(
    user_id bigint NOT NULL,
    screen_name text COLLATE pg_catalog."default",
    name text COLLATE pg_catalog."default",
    followers_count integer,
    friends_count integer,
    favourites_count integer,
    statuses_count integer,
    verified boolean,
    location text COLLATE pg_catalog."default",
    time_zone text COLLATE pg_catalog."default",
    created_at text COLLATE pg_catalog."default",
    CONSTRAINT users_pkey PRIMARY KEY (user_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.users
    OWNER to postgres;

#Conversation's Table
-- Table: public.conversations

-- DROP TABLE IF EXISTS public.conversations;

CREATE TABLE IF NOT EXISTS public.conversations
(
    conversation_id bigint NOT NULL,
    user_id bigint NOT NULL,
    tweet_id bigint NOT NULL,
    conversation_length integer NOT NULL,
    airline text COLLATE pg_catalog."default",
    sentiment_start text COLLATE pg_catalog."default",
    sentiment_start_score real,
    sentiment_end text COLLATE pg_catalog."default",
    sentiment_end_score real,
    CONSTRAINT conversations_pkey PRIMARY KEY (conversation_id, tweet_id),
    CONSTRAINT conversation_id_tweet_id_unique UNIQUE (conversation_id, tweet_id),
    CONSTRAINT conversations_tweet_id_fkey FOREIGN KEY (tweet_id)
        REFERENCES public.tweets (tweet_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT conversations_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES public.users (user_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.conversations
    OWNER to postgres;

#Unique Locations - DELETED HOWEVER USED AT TO CREATE GEOCODED-DATA TABLE (unncessary)
CREATE TABLE unique_locations AS
SELECT DISTINCT TRIM(LOWER(location)) AS normalized_location
FROM users
WHERE location IS NOT NULL AND LENGTH(TRIM(location)) > 0;

#geocoded location
-- Table: public.geocoded_locations

-- DROP TABLE IF EXISTS public.geocoded_locations;

CREATE TABLE IF NOT EXISTS public.geocoded_locations
(
    normalized_location text COLLATE pg_catalog."default" NOT NULL,
    latitude double precision,
    longitude double precision,
    confidence text COLLATE pg_catalog."default",
    region text COLLATE pg_catalog."default",
    CONSTRAINT geocoded_locations_pkey PRIMARY KEY (normalized_location)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.geocoded_locations
    OWNER to postgres;

#user_region_map
-- Table: public.user_region_map

-- DROP TABLE IF EXISTS public.user_region_map;

CREATE TABLE IF NOT EXISTS public.user_region_map
(
    user_id bigint,
    region text COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.user_region_map
    OWNER to postgres;

-- Table: public.user_location_map

-- DROP TABLE IF EXISTS public.user_location_map;

CREATE TABLE IF NOT EXISTS public.user_location_map
(
    user_id bigint,
    normalized_location text COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.user_location_map
    OWNER to postgres;