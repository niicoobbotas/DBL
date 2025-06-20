### 🐍 Python Version  
This project was created with **Python 3.12.5**.  
Download it here: <https://www.python.org/downloads/release/python-3125/>  

## ⚙️ 1. Install Dependencies

```bash
python -m pip install "pandas==2.2.2" "matplotlib==3.8.4" "tqdm==4.66.4" "transformers==4.41.2" "geopy==2.4.1" "reverse_geocoder==1.5.1" "plotly==5.21.0" "sqlalchemy==2.0.30" "psycopg2-binary==2.9.9" "scipy==1.13.1" "numpy==1.26.4"
```

> **Note:**  
> * `transformers` will download the sentiment‑analysis model on first use (requires internet).  
> * `sqlalchemy` + `psycopg2` are used only to **connect** to the pre‑existing database.
> * The files include input paths and output paths, please change this to the paths you are using, thanks!

---

## 2.`create table scripts.py` 
This python file includes all the SQL code used to create the database, creating this database again would require the setup of another online AWS server. Therefore, the files you are about to run include the necessary code to connect to the current set-up database.

## 🗂️ 3. Execution Order & Script Purpose

| # | Script | Purpose | Outputs |
|---|--------|---------|---------|
| 1 | **Cleaned Final Code.py** | Cleans raw tweets, removes spam/weird accounts | `Cleaned Dataset/*.json` |
| 2 | **conversation extraction.py** | Reconstructs user ↔ airline conversations | `extracted_conversations/*.json` |
| 3 | **conversationsbutindividualtweets.py** | Collects **non‑airline** tweets for sentiment analysis | `all_non_airline_tweets.json` |
| 4 | **sentimentanalysis.py** | Adds sentiment analysis to user conversations tweets | `all_non_airline_tweets_with_sentiment.json` |
| 5 | **conversations_with_sentiment.py** | Merges sentiment back into full conversations | `conversations_with_sentiment/*.json` |
| 6 | **Upload users and tweets to db.py** | Bulk‑loads users and tweets into PostgreSQL tables `users` and `tweets` | Rows inserted into DB | (Running won't give a visual output)
| 7 | **conversations upload.py** | Bulk‑loads conversation‑level data (with sentiment) into table `conversations` | Rows inserted into DB | (Running won't give a visual output)
| 8 | **sentiment_sankey.py** | Sankey diagram of sentiment flow (all airlines) | `sentiment_sankey.html` |
| 9 | **sentiment_sankey_lufthansa.py** | Same Sankey but filtered to Lufthansa | `sentiment_sankey_lufthansa.html` |
| 10 | **conversations_per_airline.py** | Bar‑chart of conversation counts per airline | `conversations_per_airline.png` |
| 11 | **LUFTHANSA CONVOS PER REGION.py** | Bar‑chart of Lufthansa conversation counts per user region | Displays matplotlib bar chart |
| 12 | **T‑Test Sentiment Evolution.py** | Welch t‑tests + boxplots of sentiment change by region & airline | Two matplotlib windows |
| 13 | **geocoding the data.py** | Geocode free‑text locations | `geocoded_locations.csv` |
| 14 | **turning geocoded data to regions.py** | Map lat/lon → country/region | `geocoded_with_region.csv` |
| 15 | **ordering the columns for geocoding.py** | Tidy geocode CSV columns | `geocoded_ordered_no_nulls_UTF-8.csv` |

---

## ▶️ 4. How to Run

1. Open a terminal **in this folder**.  
2. Run each script in sequence:

```bash
python "Cleaned Final Code.py"
python "conversation extraction.py"
python "conversationsbutindividualtweets.py"
python "sentimentanalysis.py"
python "conversations_with_sentiment.py"
python "Upload users and tweets to db.py"
python "conversations upload.py"
python "sentiment_sankey.py"
python "sentiment_sankey_lufthansa.py"
python "conversations_per_airline.py"
python "LUFTHANSA CONVOS PER REGION.py"
python "geocoding the data.py"
python "turning geocoded data to regions.py"
python "ordering the columns for geocoding.py"
```

---

## 🛡️ 5. Database Notes

* The PostgreSQL database is **already running remotely**.  
* Scripts connect via `sqlalchemy` and **read‑only** queries.  
---

## ✅ 6. Expected Results

Running all mandatory scripts will produce:

* Cleaned tweet JSON files  
* Conversation JSON with sentiment labels  
* Two interactive Sankey HTML files  
* One PNG bar chart  
* Console output with T‑test statistics & two boxplots  
* Geolocation scripts produce CSVs for location‑based analyses.
