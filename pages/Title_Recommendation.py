import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="Title Recommendation | CineHeist",page_icon="Images/favicon.ico", layout="wide")
st.title("🎥 Movie Title-Based Recommendations")

# Load dataset
@st.cache_data
def load_data():
    return pd.read_csv("dataset.csv")

movies_df = load_data()

# Precompute TF-IDF matrix for movie overviews
@st.cache_resource
def compute_tfidf_matrix(df):
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['overview'].fillna(''))  # Handle missing overviews
    return tfidf, tfidf_matrix

tfidf, tfidf_matrix = compute_tfidf_matrix(movies_df)

# Recommendation function based on movie title
def recommend_by_title(selected_movie, df, tfidf, tfidf_matrix, num_recommendations=5):
    # Get the index of the selected movie
    movie_idx = df[df['title'] == selected_movie].index[0]
    
    # Calculate cosine similarity between the selected movie and all other movies
    similarity_scores = cosine_similarity(tfidf_matrix[movie_idx], tfidf_matrix).flatten()
    
    # Get the top similar movies (excluding the selected movie itself)
    top_indices = similarity_scores.argsort()[-num_recommendations-1:][::-1]
    top_indices = [i for i in top_indices if i != movie_idx]  # Exclude the selected movie itself
    return df.iloc[top_indices][['title', 'overview', 'genre', 'vote_average', 'release_date']]

# Dropdown for movie selection
movie_titles = movies_df['title'].tolist()
selected_movie = st.selectbox("Select a Movie", movie_titles)

# Slider for number of recommendations
num_recommendations = st.slider("Number of Recommendations", 1, 10, 5)

if selected_movie:
    recommendations = recommend_by_title(selected_movie, movies_df, tfidf, tfidf_matrix, num_recommendations)
    
    if recommendations.empty:
        st.error("No recommendations found. Try selecting a different movie.")
    else:
        st.write(f"### Movies similar to **{selected_movie}**:")
        for idx, row in recommendations.iterrows():
            st.markdown(f"""
                **🎥 {row['title']}**
                - **Overview**: {row['overview']}
                - **Genres**: {row['genre']}
                - **Rating**: {row['vote_average']} / 10
                - **Release Date**: {row['release_date']}
            """)
else:
    st.info("Select a movie from the dropdown to see recommendations.")
