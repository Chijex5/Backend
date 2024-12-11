import pandas as pd
from sklearn.preprocessing import StandardScaler
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
import joblib

# Preprocess the data for the model
def preprocess_data(data):
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
    predictions = [
        (book_id, model.predict(user_id, book_id).est)
        for book_id in unique_books
    ]

    # Sort and return top recommendations
    top_recommendations = sorted(predictions, key=lambda x: x[1], reverse=True)
    return [book_id for book_id, _ in top_recommendations[:top_n]]
