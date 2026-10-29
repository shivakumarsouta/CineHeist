import streamlit as st
import pandas as pd
import urllib.parse

from recommender import (
    load_dataset,
    build_recommendation_text,
    build_embedding_model,
    recommend_by_embedding,
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Plot Recommendation | CineHeist",
    page_icon=str("images/favicon.png"),
    layout="wide",
)


# ============================================================
# CUSTOM STYLING
# ============================================================

st.markdown(
    """
    <style>
        .stApp {
            background-color: #0b0b0f;
            color: #f5f5f5;
        }

        .block-container {
            max-width: 1200px;
            padding-top: 1.5rem !important;
            padding-bottom: 3rem;
        }

        [data-testid="stSidebar"],
        [data-testid="stSidebarNav"],
        [data-testid="collapsedControl"] {
            display: none !important;
        }

        [data-testid="stHeader"] {
            display: none !important;
        }

        .brand {
            font-size: 1.7rem;
            font-weight: 800;
            color: #ff4b4b;
            letter-spacing: 1px;
            padding-top: 0.35rem;
        }

        .stButton > button {
            border-radius: 9px;
            font-weight: 600;
            min-height: 44px;
        }

        @media (max-width: 768px) {
            .brand {
                font-size: 1.35rem;
            }
        }

        /* Fixed-height plot input with internal scrolling */
        .stTextArea textarea {
            resize: none !important;
            overflow-y: auto !important;
            height: 240px !important;
            min-height: 240px !important;
            max-height: 240px !important;
            line-height: 1.6;
        }

        /* Reduce unnecessary heading spacing */
        h2, h3 {
            margin-bottom: 0.8rem !important;
        }

        /* Keep the input controls visually consistent */
        div[data-baseweb="select"] > div {
            border-radius: 8px;
        }

        .stSlider {
            padding-top: 0.3rem;
        }

        /* Make the primary action stand out without adding clutter */
        .stButton > button[kind="primary"] {
            min-height: 46px;
            font-weight: 650;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# NAVBAR
# ============================================================

nav_brand, nav_dataset, nav_home = st.columns([2, 2, 2])

with nav_brand:
    st.html('<div class="brand">🎬 CINEHEIST</div>')

with nav_dataset:
    if st.button(
        "🔍 Explore Titles",
        key="navbar_dataset",
        use_container_width=True,
    ):
        st.switch_page("pages/movie_details.py")

with nav_home:
    if st.button(
        "← Home 🏠",
        key="navbar_home",
        type="primary",
        use_container_width=True,
    ):
        st.switch_page("app.py")


# ============================================================
# PAGE INTRODUCTION
# ============================================================

st.title("✍️ Plot-Based Movie & TV Recommendations")

st.write(
    "Describe the story you want to watch, and CineHeist "
    "will recommend movies and TV shows with similar plots."
)


# ============================================================
# LOAD RECOMMENDATION DATA AND MODEL
# ============================================================


@st.cache_data
def load_recommendation_data():
    """Load the dataset and prepare recommendation text."""
    df = load_dataset()
    return build_recommendation_text(df)


@st.cache_resource
def load_recommendation_model(df):
    """Load or build the semantic embedding model."""
    return build_embedding_model(df)


try:
    df = load_recommendation_data()
    model, embeddings = load_recommendation_model(df)

except FileNotFoundError as error:
    st.error(f"Unable to load the recommendation dataset: {error}")
    st.stop()


# ============================================================
# HELPER FUNCTIONS
# ============================================================


def generate_movie_link(title):
    """Generate an IMDb search link for a title."""
    query = urllib.parse.quote(title)
    return f"https://www.imdb.com/find/?q={query}"


def get_poster_url(poster_path):
    """Return the full TMDB poster URL, if available."""

    if pd.isna(poster_path) or not str(poster_path).strip():
        return None

    return f"https://image.tmdb.org/t/p/w500{poster_path}"


# ============================================================
# USER INPUTS
# ============================================================

left_col, right_col = st.columns([7, 3], gap="large")

with left_col:
    st.subheader("📝 Your Story")

    input_plot = st.text_area(
        "Plot description",
        placeholder=(
            "Describe the story you want to watch...\n\n"
            "Example: A son fights to protect his family "
            "and seeks revenge against those who wronged them."
        ),
        height=240,
        label_visibility="collapsed",
        key="plot_description",
    )

with right_col:
    st.subheader("⚙️ Preferences")

    media_choice = st.selectbox(
        "Content type",
        ["All", "Movies", "TV Shows"],
    )

    languages = sorted(df["original_language"].dropna().unique().tolist())

    language_choice = st.selectbox(
        "Original language",
        ["All languages"] + languages,
    )

    num_recommendations = st.slider(
        "Number of results",
        min_value=1,
        max_value=10,
        value=5,
    )

st.markdown("<div style='height: 12px'></div>", unsafe_allow_html=True)

find_recommendations = st.button(
    "🎬 Find Recommendations",
    type="primary",
    use_container_width=True,
)


# ============================================================
# GENERATE RECOMMENDATIONS
# ============================================================

if find_recommendations:
    if not input_plot.strip():
        st.warning("Please enter a plot description first.")

    else:
        media_type = {
            "All": None,
            "Movies": "movie",
            "TV Shows": "tv",
        }[media_choice]

        language = None if language_choice == "All languages" else language_choice

        recommendations = recommend_by_embedding(
            query=input_plot,
            df=df,
            model=model,
            embeddings=embeddings,
            top_n=num_recommendations,
            media_type=media_type,
            language=language,
        )

        if recommendations.empty:
            st.warning(
                "No recommendations matched your filters. "
                "Try another description or language."
            )

        else:
            st.subheader("Your Recommendations")

            for _, row in recommendations.iterrows():
                title = str(row["title"])
                overview = str(row["overview"])
                genre_value = row.get("genre")

                genre = (
                    str(genre_value).strip()
                    if pd.notna(genre_value) and str(genre_value).strip()
                    else "Not available"
                )

                media_label = "Movie" if row["media_type"] == "movie" else "TV Show"

                year = row.get("year")

                year_label = str(int(year)) if pd.notna(year) else "Year unavailable"

                language_label = row.get(
                    "original_language",
                    "Unknown",
                )

                rating = row.get("vote_average")

                rating_label = (
                    f"{rating:.1f}/10" if pd.notna(rating) else "Not available"
                )

                score = row["similarity_score"]

                poster_url = get_poster_url(row.get("poster_path"))

                with st.container(border=True):
                    poster_col, details_col = st.columns([1, 3])

                    with poster_col:
                        if poster_url:
                            st.image(
                                poster_url,
                                caption=title,
                                width="stretch",
                            )
                        else:
                            st.info("Poster unavailable")

                    with details_col:
                        st.subheader(title)

                        st.caption(
                            f"{media_label} · {year_label} · Language: {language_label}"
                        )

                        st.write(f"**Genres:** {genre}")
                        # Display the cast when available.
                        cast_value = row.get("cast", "")

                        cast = str(cast_value).strip() if pd.notna(cast_value) else ""

                        if cast:
                            st.write(f"**Cast:** {cast}")
                        else:
                            st.write("**Cast:** Not available")
                        st.write(f"**Rating:** {rating_label}")
                        st.write(f"**Similarity score:** {score:.3f}")

                        st.write(
                            overview if overview else "Plot description unavailable."
                        )

                        st.link_button(
                            "Find on IMDb",
                            generate_movie_link(title),
                        )

# ==================== FOOTER ====================

st.html("""
<div style="
    text-align: center;
    border-top: 1px solid #2d2d39;
    margin-top: 3rem;
    padding: 1.5rem 0;
    color: #b5b5c0;
    line-height: 1.8;
">
    <h3 style="color: #ff4b4b; margin-bottom: 0;">
        🎬 CINEHEIST
    </h3>

    <p>
        Your Movie Matchmaker | AI-Powered Movie & TV Recommendations
    </p>

    <small>© 2026 CineHeist · Built with ❤️ using Python & Streamlit</small>
</div>
""")