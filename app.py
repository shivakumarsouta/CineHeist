import streamlit as st
import pandas as pd

from pathlib import Path


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Home | CineHeist",
    page_icon="images/favicon.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent
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

        /* Hide Streamlit sidebar and header */
        [data-testid="stSidebar"],
        [data-testid="stSidebarNav"],
        [data-testid="collapsedControl"],
        [data-testid="stHeader"] {
            display: none !important;
        }

        /* Navbar */
        .brand {
            font-size: 1.7rem;
            font-weight: 800;
            color: #ff4b4b;
            letter-spacing: 1px;
            padding-top: 0.35rem;
        }

        /* Hero */
        .hero {
            padding: 4rem 1.5rem;
            text-align: center;
            background: radial-gradient(
                ellipse at top,
                #29202b 0%,
                #141218 45%,
                #0b0b0f 100%
            );
            border: 1px solid #29232e;
            border-radius: 18px;
            margin: 1.5rem 0 3rem;
        }

        .hero h1 {
            font-size: clamp(2.5rem, 6vw, 4.5rem);
            font-weight: 800;
            line-height: 1.15;
            margin-bottom: 1.5rem;
            color: #ffffff;
        }

        .hero h1 span {
            color: #ff4b4b;
        }

        .hero-description {
            max-width: 700px;
            margin: 0 auto;
            color: #c2c2cc;
            font-size: 1.15rem;
            line-height: 1.8;
        }

        /* Section headings */
        .section-heading {
            font-size: 2rem;
            font-weight: 750;
            margin-top: 2rem;
            margin-bottom: 0.75rem;
            color: #ffffff;
        }

        .section-description {
            color: #b5b5c0;
            line-height: 1.8;
            margin-bottom: 1.5rem;
            font-size: 1rem;
        }

        /* Feature cards */
        .feature-card {
            background: #17171f;
            border: 1px solid #2d2d39;
            border-radius: 14px;
            padding: 1.4rem;
            min-height: 170px;
            margin-bottom: 1rem;
        }

        .feature-card h3 {
            color: #ff6969;
            font-size: 1.15rem;
            margin-bottom: 0.7rem;
        }

        .feature-card p {
            color: #c2c2cc;
            line-height: 1.7;
            font-size: 0.95rem;
        }

        /* Dataset metrics */
        .metric-card {
            background: #17171f;
            border: 1px solid #2d2d39;
            border-radius: 14px;
            padding: 1.5rem 1rem;
            text-align: center;
            margin-bottom: 1rem;
        }

        .metric-value {
            color: #ff6969;
            font-size: 2.2rem;
            font-weight: 800;
        }

        .metric-label {
            color: #b5b5c0;
            font-size: 0.95rem;
            margin-top: 0.4rem;
        }

        .technology-list {
            background: #17171f;
            border: 1px solid #2d2d39;
            border-radius: 12px;
            padding: 1.25rem;
            color: #d2d2dc;
            line-height: 2;
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

        @media (max-width: 768px) {
            .hero {
                padding: 3rem 1rem;
            }

            .hero h1 {
                font-size: 2.5rem;
            }

            .hero-description {
                font-size: 1rem;
            }

            .section-heading {
                font-size: 1.7rem;
            }

            .brand {
                font-size: 1.3rem;
            }

            .metric-value {
                font-size: 1.7rem;
            }
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
    """Load the CineHeist dataset."""

    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATASET_PATH}")

    return pd.read_csv(DATASET_PATH)


try:
    titles_df = load_dataset()

except FileNotFoundError as error:
    st.error(str(error))
    st.stop()


# ============================================================
# NAVBAR
# ============================================================

nav_brand, nav_details, nav_recommendations = st.columns([2, 2, 2])

with nav_brand:
    st.html('<div class="brand">🎬 CINEHEIST</div>')

with nav_details:
    if st.button(
        "🔍 Explore Titles",
        key="navbar_movie_details",
        use_container_width=True,
    ):
        st.switch_page("pages/movie_details.py")

with nav_recommendations:
    if st.button(
        "✨ Recommendations →",
        key="navbar_recommendations",
        type="primary",
        use_container_width=True,
    ):
        st.switch_page("pages/recommendation_page.py")


# ============================================================
# HERO SECTION
# ============================================================

st.html(
    """
    <div class="hero">
        <h1>
            Your Next Favorite Story<br>
            Starts with <span>CineHeist</span>
        </h1>

        <div class="hero-description">
            Discover movies and TV shows that match your interests.
            Describe a story, mood, or concept, and let semantic
            search help you find your next watch.
        </div>
    </div>
    """
)


# ============================================================
# ABOUT CINEHEIST
# ============================================================

st.html(
    """
    <div class="section-heading">What is CineHeist?</div>

    <div class="section-description">
        CineHeist is a movie and TV show discovery application
        built with Python and Streamlit. It uses semantic similarity
        to understand plot descriptions and recommend titles with
        related stories, themes, and concepts.
    </div>
    """
)


# ============================================================
# FEATURES
# ============================================================

feature_columns = st.columns(3)

features = [
    (
        "🎯 Plot-Based Discovery",
        "Describe the kind of story you want to watch and discover "
        "titles with similar themes and concepts.",
    ),
    (
        "🧠 Semantic Search",
        "Text embeddings help identify meaningful similarities "
        "between plot descriptions.",
    ),
    (
        "🌍 Content & Language Filters",
        "Narrow your recommendations by content type and original "
        "language to discover titles that suit your preferences.",
    ),
]

for column, (title, description) in zip(
    feature_columns,
    features,
):
    with column:
        st.html(
            f"""
            <div class="feature-card">
                <h3>{title}</h3>
                <p>{description}</p>
            </div>
            """
        )


# ============================================================
# DATASET OVERVIEW
# ============================================================

st.divider()

st.html(
    """
    <div class="section-heading">Inside the CineHeist Collection</div>

    <div class="section-description">
        A quick look at the movies and TV shows powering
        CineHeist's discovery and recommendation features.
    </div>
    """
)

total_titles = len(titles_df)

movie_count = (
    int(titles_df["media_type"].eq("movie").sum())
    if "media_type" in titles_df.columns
    else 0
)

tv_count = (
    int(titles_df["media_type"].eq("tv").sum())
    if "media_type" in titles_df.columns
    else 0
)

metric_columns = st.columns(3)

metrics = [
    (metric_columns[0], total_titles, "Total Titles"),
    (metric_columns[1], movie_count, "Movies"),
    (metric_columns[2], tv_count, "TV Shows"),
]

for column, value, label in metrics:
    with column:
        st.html(
            f"""
            <div class="metric-card">
                <div class="metric-value">{value:,}</div>
                <div class="metric-label">{label}</div>
            </div>
            """
        )


# ============================================================
# TECHNOLOGY STACK
# ============================================================

st.divider()

st.html(
    """
    <div class="section-heading">Built With</div>

    <div class="technology-list">
        Python &nbsp; · &nbsp;
        Streamlit &nbsp; · &nbsp;
        Pandas &nbsp; · &nbsp;
        NumPy &nbsp; · &nbsp;
        Sentence Transformers &nbsp; · &nbsp;
        Scikit-learn &nbsp; · &nbsp;
        TMDB metadata
    </div>
    """
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

    <p>
        Designed & Developed by <strong>Shiva Kumar Souta</strong>
    </p>

    <p>
        <a href="https://github.com/shivakumarsouta/CineHeist"
           target="_blank" style="color: #ff6969;">GitHub</a>
        &nbsp; · &nbsp;
        <a href="https://www.linkedin.com/in/shivakumarsouta"
           target="_blank" style="color: #ff6969;">LinkedIn</a>
        &nbsp; · &nbsp;
        <a href="https://shivakumarsouta-portfolio.vercel.app"
           target="_blank" style="color: #ff6969;">Portfolio</a>
    </p>

    <small>© 2026 CineHeist · Built with ❤️ using Python & Streamlit</small>
</div>
""")