
import mysql.connector
import pandas as pd
from sklearn.preprocessing import StandardScaler
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
import joblib
from dotenv import load_dotenv
import os
load_dotenv()

# Database connection
def connect_to_db():
    return mysql.connector.connect(
        host=os.getenv('MYSQL_HOST'),
        user= os.getenv('MAIL_USERNAME'),
        password= os.getenv('MAIL_PASSWORD'),
        port=int(os.getenv('MAIL_PORT')),
        database= os.getenv('MYSQL_DB')
    )

# Fetch purchases and books data
def fetch_user_data(user_id):
    conn = connect_to_db()
    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch purchases
        query_purchases = "SELECT * FROM purchases WHERE userId = %s"
        cursor.execute(query_purchases, (user_id,))
        purchases = pd.DataFrame(cursor.fetchall())

        # Fetch books
        query_books = "SELECT * FROM books"
        cursor.execute(query_books)
        books = pd.DataFrame(cursor.fetchall())

        # Merge purchases with books to get details
        data = purchases.merge(books, left_on="bookId", right_on="id")
        return data

    except Exception as e:
        print(f"Error fetching user data: {e}")
    finally:
        cursor.close()
        conn.close()

# Preprocess the data for model
def preprocess_data(data):
    # Scale numerical features
    scaler = StandardScaler()
    data['price_scaled'] = scaler.fit_transform(data[['price_y']])
    data['views_scaled'] = scaler.fit_transform(data[['views']])
    data['rating_scaled'] = scaler.fit_transform(data[['rating']])
    return data, scaler

# Load recommendation model
def load_model(filename="collaborative_model.pkl"):
    return joblib.load(filename)

# Make predictions using the collaborative model
def get_recommendations(user_id, data, top_n=5):
    reader = Reader(rating_scale=(1, 5))
    interaction_data = data[['userId', 'bookId', 'rating']]
    dataset = Dataset.load_from_df(interaction_data, reader)
    trainset, _ = train_test_split(dataset, test_size=0.2)

    # Load or train the collaborative model
    model = load_model()
    model.fit(trainset)

    # Predict ratings for all books
    unique_books = data['bookId'].unique()
    predictions = []
    for book_id in unique_books:
        predictions.append((book_id, model.predict(user_id, book_id).est))

    # Sort by predicted ratings
    predictions = sorted(predictions, key=lambda x: x[1], reverse=True)
    top_recommendations = [book_id for book_id, _ in predictions[:top_n]]
    return top_recommendations

# Fetch book details from database based on recommendations
# Fetch book details from database based on recommendations
def fetch_book_details(book_ids):
    # Convert book_ids to a list of standard Python integers
    book_ids = [int(book_id) for book_id in book_ids]

    conn = connect_to_db()
    query_books = f"SELECT * FROM books WHERE id IN ({', '.join(map(str, book_ids))})"
    books = pd.read_sql(query_books, conn)
    conn.close()
    return books

# Main function
def get_recommendation(user_id):

    print("Fetching user data...")
    data = fetch_user_data(user_id)

    print("Preprocessing data...")
    processed_data, _ = preprocess_data(data)

    print("Generating recommendations...")
    recommended_book_ids = get_recommendations(user_id, processed_data)
    return recommended_book_ids
