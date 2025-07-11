import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import urllib.parse

st.set_page_config(page_title="Plot Recommendation | CineHeist",page_icon="Images/favicon.ico", layout="wide")
st.title("🎥 Plot-Based Movie Recommendations")


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

# Recommendation function based on plot similarity
def recommend_by_plot(input_plot, df, tfidf, tfidf_matrix, num_recommendations=5):
    input_vector = tfidf.transform([input_plot])
    similarity_scores = cosine_similarity(input_vector, tfidf_matrix).flatten()
    top_indices = similarity_scores.argsort()[-num_recommendations:][::-1]
    return df.iloc[top_indices][['title', 'overview', 'genre', 'vote_average', 'release_date']]

# Function to generate links dynamically (e.g., IMDb or TMDb)
def generate_movie_link(title):
    base_url = "https://www.imdb.com/find?q="
    query = urllib.parse.quote(title)  # URL encode the title
    return f"{base_url}{query}"

# Dynamic CSS for consistent styling
st.markdown("""
    <style>
        .main-header {
            background-color: var(--secondary-background-color);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .main-header h1, .main-header p {
            color: var(--primary-color);
        }
        .movie-box {
            background-color: var(--background-color-secondary);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1);
        }
        .movie-box h4 {
            margin: 0 0 10px;
        }
        .movie-box p {
            margin: 5px 0;
        }
        .movie-link {
            color: var(--primary-color);
            text-decoration: none;
        }
        .movie-link:hover {
            text-decoration: underline;
        }
    </style>
""", unsafe_allow_html=True)

# App Header

# Input Section
st.write("### Enter a Plot Description to Find Similar Movies")
input_plot = st.text_area("Describe your desired movie plot:", placeholder="E.g., A group of friends on a quest to destroy a magical ring.")
num_recommendations = st.slider("Number of Recommendations", 1, 10, 5)

# Recommendations Section
if input_plot:
    recommendations = recommend_by_plot(input_plot, movies_df, tfidf, tfidf_matrix, num_recommendations)
    if recommendations.empty:
        st.error("No recommendations found. Try refining your plot description.")
    else:
        st.write("### Recommended Movies:")
        for idx, row in recommendations.iterrows():
            movie_link = generate_movie_link(row['title'])  # Generate link for each movie
            with st.container():
                st.markdown(f"""
                    <div class="movie-box">
                        <h4>🎥 <a class="movie-link" href="{movie_link}" target="_blank">{row['title']}</a></h4>
                        <p><strong>Overview:</strong> {row['overview']}</p>
                        <p><strong>Genres:</strong> {row['genre']}</p>
                        <p><strong>Rating:</strong> {row['vote_average']} / 10</p>
                        <p><strong>Release Date:</strong> {row['release_date']}</p>
                    </div>
                """, unsafe_allow_html=True)
else:
    st.info("Enter a plot description or try the example above.")
