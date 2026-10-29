import os
from pathlib import Path
from urllib.parse import quote
from html import escape

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv
import unicodedata


# ============================================================
# PAGE CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

st.set_page_config(
    page_title="Explore Titles | CineHeist",
    page_icon=str("images/favicon.png"),
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================

load_dotenv(PROJECT_ROOT / ".env")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"
DATASET_PATH = PROJECT_ROOT / "data" / "titles.csv"


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
        [data-testid="collapsedControl"],
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

        .page-heading {
            font-size: 2.5rem;
            font-weight: 800;
            margin-top: 2rem;
            margin-bottom: 0.5rem;
            color: #ffffff;
        }

        .page-description {
            color: #b5b5c0;
            line-height: 1.8;
            margin-bottom: 2rem;
        }

        .detail-card {
            background: #17171f;
            border: 1px solid #2d2d39;
            border-radius: 14px;
            padding: 1.5rem;
            margin-top: 1rem;
        }

        .detail-title {
            font-size: 2rem;
            font-weight: 800;
            color: #ffffff;
            margin-bottom: 0.75rem;
        }

        .detail-meta {
            color: #b5b5c0;
            line-height: 1.9;
        }

        .overview {
            color: #dedee6;
            font-size: 1rem;
            line-height: 1.9;
        }

        .section-heading {
            font-size: 1.5rem;
            font-weight: 750;
            color: #ffffff;
            margin-top: 2rem;
            margin-bottom: 1rem;
        }

        .footer {
            text-align: center;
            color: #858591;
            border-top: 1px solid #292932;
            margin-top: 4rem;
            padding-top: 1.5rem;
            line-height: 1.8;
        }

        .stButton > button {
            border-radius: 9px;
            font-weight: 600;
            min-height: 44px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LOAD DATASET
# ============================================================


@st.cache_data
def load_dataset():
    """Load movie and TV show metadata from the local CSV."""
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATASET_PATH}")

    df = pd.read_csv(DATASET_PATH)

    if "title" not in df.columns:
        raise ValueError("The dataset does not contain a 'title' column.")

    df = df.copy()
    df["title"] = df["title"].fillna("").astype(str)
    return df


try:
    titles_df = load_dataset()
except (FileNotFoundError, ValueError) as error:
    st.error(str(error))
    st.stop()


# ============================================================
# HELPER FUNCTIONS
# ============================================================


def normalize_title(title):
    """Normalize titles for accent-insensitive searching."""

    title = unicodedata.normalize("NFKD", str(title))

    title = "".join(
        character for character in title if not unicodedata.combining(character)
    )

    return title.casefold().strip()


def get_value(row, column, default="Not available"):
    """Safely retrieve a value from a dataset row."""
    value = row.get(column, default)

    if pd.isna(value) or str(value).strip() == "":
        return default

    return value


def get_year(row):
    """Get the release year from available dataset columns."""
    year = row.get("year")

    if pd.notna(year) and str(year).strip():
        try:
            return str(int(float(year)))
        except (ValueError, TypeError, OverflowError):
            pass

    release_date = row.get("release_date")

    if pd.notna(release_date) and str(release_date).strip():
        return str(release_date)[:4]

    return "Year unavailable"


def get_poster_url(poster_path):
    """Build a TMDB image URL from a poster path."""
    if pd.isna(poster_path) or not str(poster_path).strip():
        return None

    poster_path = str(poster_path).strip()

    if poster_path.startswith("http"):
        return poster_path

    return f"{TMDB_IMAGE_URL}{poster_path}"


def get_imdb_url(row):
    """Create an IMDb link when an IMDb ID is available."""
    imdb_id = row.get("imdb_id")

    if pd.notna(imdb_id) and str(imdb_id).strip():
        return f"https://www.imdb.com/title/{str(imdb_id).strip()}/"

    title = str(get_value(row, "title", ""))
    return f"https://www.imdb.com/find/?q={quote(title)}"


def format_runtime(runtime):
    """Convert runtime in minutes into hours and minutes."""
    if runtime is None:
        return "Not available"

    try:
        runtime = int(runtime)
        if runtime <= 0:
            return "Not available"

        hours, minutes = divmod(runtime, 60)
        return f"{hours}h {minutes}m" if hours else f"{minutes}m"
    except (ValueError, TypeError):
        return "Not available"


# ============================================================
# TMDB API
# ============================================================


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_tmdb_details(media_type, tmdb_id):
    """Fetch additional details from TMDB and cache the response."""
    if not TMDB_API_KEY or media_type not in {"movie", "tv"}:
        return None

    try:
        tmdb_id = int(tmdb_id)

        response = requests.get(
            f"{TMDB_BASE_URL}/{media_type}/{tmdb_id}",
            params={
                "api_key": TMDB_API_KEY,
                "append_to_response": "credits",
            },
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    except (requests.RequestException, ValueError, TypeError):
        return None


def display_tmdb_details(details):
    """Display supplementary information returned by TMDB."""
    st.html('<div class="section-heading">Additional Details</div>')

    runtime = details.get("runtime")
    if not runtime and details.get("episode_run_time"):
        runtimes = details["episode_run_time"]
        if runtimes:
            runtime = runtimes[0]

    info_columns = st.columns(4)

    with info_columns[0]:
        st.metric("Runtime", format_runtime(runtime))
    with info_columns[1]:
        st.metric("Status", details.get("status") or "Not available")
    with info_columns[2]:
        st.metric("Seasons", details.get("number_of_seasons") or "Not available")
    with info_columns[3]:
        st.metric("Episodes", details.get("number_of_episodes") or "Not available")

    credits = details.get("credits", {})
    cast = credits.get("cast", [])
    crew = credits.get("crew", [])

    directors = [
        person.get("name")
        for person in crew
        if person.get("job") == "Director" and person.get("name")
    ]
    creators = [
        person.get("name")
        for person in details.get("created_by", [])
        if person.get("name")
    ]

    if directors:
        st.write("**Director:** " + ", ".join(directors[:3]))
    elif creators:
        st.write("**Creator:** " + ", ".join(creators[:3]))

    cast_names = [person.get("name") for person in cast[:8] if person.get("name")]
    if cast_names:
        st.write("**Cast:** " + ", ".join(cast_names))

    genre_names = [
        genre.get("name") for genre in details.get("genres", []) if genre.get("name")
    ]
    if genre_names:
        st.write("**TMDB Genres:** " + ", ".join(genre_names))

    homepage = details.get("homepage")
    if homepage and homepage.startswith(("https://", "http://")):
        st.link_button("Official Website", homepage)


# ============================================================
# NAVBAR
# ============================================================

nav_brand, nav_home, nav_recommendations = st.columns([2, 2, 2])

with nav_brand:
    st.html('<div class="brand">🎬 CINEHEIST</div>')

with nav_home:
    if st.button("← Home 🏠", key="details_home", use_container_width=True):
        st.switch_page("app.py")

with nav_recommendations:
    if st.button(
        "✨ Recommendations →",
        key="details_recommendations",
        type="primary",
        use_container_width=True,
    ):
        st.switch_page("pages/recommendation_page.py")


# ============================================================
# PAGE INTRODUCTION
# ============================================================

st.html(
    """
    <div class="page-heading">Explore Movies & TV Shows</div>
    <div class="page-description">
        Enter a movie or TV show title to view its details.
    </div>
    """
)


# ============================================================
# SEARCH BY TITLE
# ============================================================

with st.form("title_search_form"):
    search_query = st.text_input(
        "Movie or TV show name",
        placeholder="Example: Bāhubali",
    ).strip()

    search_clicked = st.form_submit_button(
        "🔍 Search",
        type="primary",
        use_container_width=True,
    )

if search_clicked:
    if not search_query:
        st.warning("Please enter a movie or TV show name.")
        st.stop()

    normalized_query = normalize_title(search_query)

    normalized_titles = titles_df["title"].apply(normalize_title)

    # Try an exact match first.
    matching_titles = titles_df[normalized_titles == normalized_query]

    # If no exact match exists, search for partial title matches.
    if matching_titles.empty:
        matching_titles = titles_df[
            normalized_titles.str.contains(
                normalized_query,
                regex=False,
                na=False,
            )
        ]

    if matching_titles.empty:
        st.error(
            f'No movie or TV show found with the title "{search_query}". Please check the spelling on TMDB'
        )
        st.stop()

    # If multiple entries share a title, prefer the first dataset match.
    selected_row = matching_titles.iloc[0]

    # ========================================================
    # DISPLAY SELECTED TITLE
    # ========================================================

    title = str(get_value(selected_row, "title", "Untitled"))
    overview = str(
        get_value(
            selected_row,
            "overview",
            "No plot overview is available.",
        )
    )
    media_type = str(get_value(selected_row, "media_type", "Unknown"))
    year = get_year(selected_row)
    genre = str(get_value(selected_row, "genre"))
    language = str(get_value(selected_row, "original_language"))
    rating = selected_row.get("vote_average")
    vote_count = selected_row.get("vote_count")
    poster_url = get_poster_url(selected_row.get("poster_path"))

    st.divider()

    poster_column, details_column = st.columns([1, 2.2])

    with poster_column:
        if poster_url:
            st.image(poster_url, width="stretch")
        else:
            st.info("Poster unavailable for this title.")

    with details_column:
        st.html(
            f"""
            <div class="detail-card">
                <div class="detail-title">{escape(title)}</div>
                <div class="detail-meta">
                    <strong>Type:</strong> {escape(media_type.upper())}<br>
                    <strong>Year:</strong> {escape(year)}<br>
                    <strong>Genres:</strong> {escape(genre)}<br>
                    <strong>Original language:</strong> {escape(language)}
                </div>
            </div>
            """
        )

        metric_columns = st.columns(2)

        with metric_columns[0]:
            if pd.notna(rating):
                st.metric("⭐ Rating", f"{float(rating):.1f}/10")
            else:
                st.metric("⭐ Rating", "Not available")

        with metric_columns[1]:
            if pd.notna(vote_count):
                st.metric("Vote Count", f"{int(vote_count):,}")
            else:
                st.metric("Vote Count", "Not available")

        st.html(
            f"""
            <div class="section-heading">Overview</div>
            <div class="overview">{escape(overview)}</div>
            """
        )

        st.link_button("Find on IMDb", get_imdb_url(selected_row))

    # ========================================================
    # ADDITIONAL TMDB INFORMATION
    # ========================================================

    tmdb_id = selected_row.get("id")

    if tmdb_id is None or pd.isna(tmdb_id) or not str(tmdb_id).strip():
        tmdb_id = selected_row.get("tmdb_id")

    if tmdb_id is not None and pd.notna(tmdb_id):
        if TMDB_API_KEY:
            with st.spinner("Loading additional title details..."):
                tmdb_details = fetch_tmdb_details(media_type, tmdb_id)

            if tmdb_details:
                display_tmdb_details(tmdb_details)
            else:
                st.info("Additional TMDB details are unavailable for this title.")
        else:
            st.caption(
                "TMDB_API_KEY was not found in the project's .env file. "
                "Additional TMDB details are disabled."
            )
    else:
        st.caption(
            "A TMDB ID is not available for this dataset entry, "
            "so additional TMDB details cannot be retrieved."
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