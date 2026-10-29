# 🎬 CineHeist: Your Movie Matchmaker

CineHeist is a movie and TV show discovery and recommendation web application built with **Python and Streamlit**.

Describe a story you want to watch, and CineHeist uses semantic similarity to recommend movies and TV shows with related plots, themes, and concepts. You can also explore individual titles, view available metadata, and discover cast information.

## ✨ Features

* **Plot-Based Recommendations:** Describe a story to discover movies and TV shows with similar plots.
* **Semantic Search:** Uses Sentence Transformers to identify meaningful similarities between descriptions.
* **Content Type Filtering:** Choose movies, TV shows, or both.
* **Language Filtering:** Filter recommendations by their original language.
* **Movie Posters:** View available posters alongside recommendations.
* **Cast Information:** View available cast details on recommendation cards.
* **Ratings and Details:** Explore ratings, release years, genres, and plot summaries.
* **Title Search:** Search for movies and TV shows in the included dataset.
* **TMDB Integration:** Retrieve additional title information, including runtime, cast, and other metadata when available.
* **IMDb Links:** Quickly find titles on IMDb.
* **Dataset Overview:** View collection statistics and a popular-genres chart on the homepage.

## 🛠️ Tech Stack

* **Python:** Core programming language.
* **Streamlit:** Web application and interactive interface.
* **Pandas:** Dataset loading and manipulation.
* **NumPy:** Numerical operations and embedding arrays.
* **Scikit-learn:** Cosine similarity calculations.
* **Sentence Transformers:** Semantic text embeddings using `all-MiniLM-L6-v2`.
* **Matplotlib:** Dataset visualization.
* **Requests:** HTTP requests to the TMDB API.
* **python-dotenv:** Loading environment variables from `.env`.
* **TMDB:** Source of movie and TV show metadata.

## 🧠 How It Works

1. CineHeist loads movie and TV show metadata from `data/titles.csv`.
2. It combines title names, plot descriptions, genres, keywords, cast, and director information into recommendation text.
3. Sentence Transformers converts the text into numerical embeddings.
4. The embeddings are cached locally to avoid regenerating them when the dataset has not changed.
5. When a user enters a plot description, CineHeist generates an embedding for the query.
6. Cosine similarity ranks titles according to how closely their embeddings match the query.
7. Optional content type and original language filters narrow the recommendations.
8. The title-details page uses the local dataset and can retrieve additional information through the TMDB API when a valid API key and matching title ID are available.

> **Note:** Similarity scores indicate semantic similarity, not a guaranteed measure of recommendation quality.

## 📂 Project Structure

```text
CineHeist/
├── app.py
├── recommender.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example                
├── images/
│   └── favicon.png
├── data/
│   └── titles.csv
└── pages/
    ├── movie_details.py
    └── recommendation_page.py
```

The exact files present locally may vary. The generated embedding files are created by the application and should not be committed to Git.

The `.env` file contains local secrets and must never be committed. The `.env.example` file documents the required environment variable without containing the actual API key.

## 🚀 How to Run Locally

### Prerequisites

* Python 3.11 or a compatible Python version.
* Git.
* An internet connection to install dependencies and download the pretrained embedding model when needed.

### 1. Clone the Repository

```bash
git clone https://github.com/shivakumarsouta/CineHeist.git
cd CineHeist
```

### 2. Create and Activate a Virtual Environment

**Windows PowerShell:**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure the TMDB API Key

Create a `.env` file in the project root:

```dotenv
TMDB_API_KEY=your_actual_tmdb_api_key
```

Replace the placeholder with your own API key.

Keep `.env` private and never commit it to GitHub.

The application can use the included dataset without a TMDB API key, but additional live TMDB details will be unavailable.

### 5. Launch CineHeist

```bash
streamlit run app.py
```

Streamlit will provide a local URL to open the application in your browser.

### First Run

On the first run, Sentence Transformers may download the pretrained `all-MiniLM-L6-v2` model.

CineHeist generates and saves title embeddings if a valid local cache is not available. Subsequent runs can reuse the cache when the dataset has not changed.

## 📊 Dataset

CineHeist uses a movie and TV show dataset stored in `data/titles.csv`.

Depending on availability, the dataset includes:

* Title and original title.
* Movie or TV show classification.
* Plot overview and tagline.
* Genres and keywords.
* Cast and director.
* Release date and year.
* Ratings and popularity.
* Original language.
* Poster paths.
* Title identifiers.

This metadata supports title discovery and metadata-aware semantic recommendations.

## 🔐 Security

* Never commit `.env` or expose your TMDB API key.
* Keep `.env.example` limited to placeholder values.
* Do not commit generated embedding files.
* Configure deployment secrets securely in the hosting platform when live API access is required.

## 🌐 Live Demo

Try CineHeist online:

**[Launch CineHeist](https://cineheist.streamlit.app/)**

## 👨‍💻 Author

**Shivakumar Souta**

* **LinkedIn:** [linkedin.com/in/shivakumarsouta](https://www.linkedin.com/in/shivakumarsouta)
* **Portfolio:** [shivakumarsouta-portfolio.vercel.app](https://shivakumarsouta-portfolio.vercel.app)
* **Email:** [shivakumarsouta18@gmail.com](mailto:shivakumarsouta18@gmail.com)