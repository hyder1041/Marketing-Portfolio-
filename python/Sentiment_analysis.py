# Sentiment analysis script using nltk
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import pandas
import pyodbc
from bisect import bisect_right
from typing import List, Tuple

# Ensure the necessary NLTK resources are downloaded
nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

def fetch_data_from_db(connection_string, query):
    """Fetch data from the database."""
    conn = pyodbc.connect(connection_string)
    df = pandas.read_sql(query, conn)
    conn.close()
    return df
def analyze_sentiment(text):
    """Analyze sentiment of the given text."""
    scores = sia.polarity_scores(text)
    return scores['compound'] #, scores['neg'], scores['neu'], scores['pos']
def categorize_sentiment(score: float, rating: int) -> str:
    """Categorize sentiment based on compound score and rating."""
    if score > 0.05:
        s = "pos"
    elif score < -0.05:
        s = "neg"
    else:
        s = "neu"
    # Bucket the rating
    if rating >= 4:
        r = "high"
    elif rating <= 2:
        r = "low"
    else:
        r = "neutral"
    # Lookup table
    table : dict[str, dict[str, str]] = {
        "pos": {
            "high": "Positive",
            "neutral": "Mixed Positive",
            "low": "Mixed Negative",
        },
        "neg": {
            "high": "Mixed Positive",
            "neutral": "Mixed Negative",
            "low": "Negative",
        },
        "neu": {
            "high": "Positive",
            "neutral": "Neutral",
            "low": "Negative",
        },
    }
    return table[s][r]
# Define sentiment boundaries and labels for bucketing
_BOUNDARIES: List[float] = [-0.5, 0.0, 0.5]
_LABELS: List[str] = [
    "-1.0 to -0.5",   # index 0
    "-0.49 to 0.0",   # index 1
    "0.0 to 0.49",    # index 2
    "0.5 to 1.0",     # index 3
]
def bucket_sentiment(score: float) -> str:
    """Bucket the sentiment score into defined ranges."""
    if not isinstance(score, (int,float)):
        raise TypeError("Score must be a number.")
    # Clamp score to the range [-1.0, 1.0]
    score = max(min(score, 1.0), -1.0)
    # Find the appropriate bucket
    # Use bisect_right to find the index
    index = bisect_right(_BOUNDARIES, score)
    return _LABELS[index]
def main():
    # Database connection string and query
    connection_string = 'DRIVER={SQL Server};SERVER=LAPTOP\\SQLEXPRESS01;DATABASE=PortfolioProject_MarketingAnalytics;Trusted_Connection=yes;'
    #query = 'SELECT ReviewID, CustomerID, ProductID, ReviewDate, Rating, ReviewText FROM fact_customer_review'
    query = '''SELECT 
                ReviewID,
	            CustomerID,
	            ProductID,
	            ReviewDate,
	            Rating,
	            REPLACE (ReviewText, '  ', ' ') AS ReviewText
            FROM
	            dbo.customer_reviews'''

    # Fetch data from the database
    customer_reviews_df = fetch_data_from_db(connection_string, query)

    # Analyze sentiment for each review
    customer_reviews_df['SentimentScore'] = customer_reviews_df['ReviewText'].apply(analyze_sentiment)
    customer_reviews_df['SentimentCategory'] = customer_reviews_df.apply(
        lambda row: categorize_sentiment(row['SentimentScore'], row['Rating']), axis=1
    )
    customer_reviews_df['SentimentBucket'] = customer_reviews_df['SentimentScore'].apply(bucket_sentiment)
    # Display the results
    print(customer_reviews_df.head())
    # Optionally, save the results to a new table or file
    # customer_reviews_df.to_sql('fact_customer_reviews_with_sentiment', conn, if_exists='replace', index=False)
    customer_reviews_df.to_csv('customer_reviews_with_sentiment.csv', index=False)
    # For demonstration, we will just print the first few rows
if __name__ == "__main__":
    main()