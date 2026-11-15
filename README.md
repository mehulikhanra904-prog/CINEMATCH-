# 🎬 CineMatch — Movie Discovery & Recommendation System

> Discover movies, explore similar titles, and build your personal watchlist.

<p align="center">
  <a href="https://cinematch-git-pyqhwbfjket6brjei4aebs.streamlit.app/"><strong>🚀 Live Demo — Try CineMatch</strong></a>
  &nbsp;·&nbsp;
  <a href="https://github.com/mehulikhanra904-prog/CINEMATCH-">GitHub Repository</a>
</p>

CineMatch is a Streamlit-based movie discovery application featuring a content-based recommendation engine. It helps users explore a movie catalog, search and filter titles, discover similar movies, and save movies to a watchlist. Optional integrations extend the experience with live movie data from TMDB and persistent, per-user watchlists through Supabase.

**Live application:** https://cinematch-git-pyqhwbfjket6brjei4aebs.streamlit.app/

> **Note:** The bundled `data/movies.csv` is a curated demo catalog. Recommendations are content-based; they are not trained on collaborative user-rating or viewing-history data.

## ✨ Features

### Movie discovery
- Search movies by title, genre, and plot overview.
- Filter the catalog by genre.
- Sort movies by rating, release year, or title.
- Browse movie cards with poster, genre, year, and rating.
- Graceful poster fallbacks and friendly empty/error states.

### Recommendation engine
- Find movies similar to a selected title.
- Display similarity scores for ranked recommendations.
- Apply optional genre and minimum-rating filters.
- Uses TF-IDF text features and cosine similarity for explainable recommendations.

### Watchlists and optional integrations
- Session-based watchlist in the core app.
- Optional Supabase authentication and persistent, per-user watchlists.
- Optional TMDB live discovery, movie details, posters, and YouTube trailer links.
- Optional integrations can be enabled through Streamlit Secrets; the basic app can run without them.

## 🧠 How the recommendation engine works

1. Combines each movie's genre information and overview into a text feature.
2. Converts the text into numerical vectors using **TF-IDF**, including unigram and bigram features.
3. Calculates similarity between movie vectors using **cosine similarity**.
4. Ranks candidate movies and applies optional genre and rating filters.

The similarity percentage represents textual similarity between movie descriptions and genres. It is **not** a probability or guarantee that a user will enjoy a movie.

## 🛠️ Tech stack

| Area | Technologies |
|---|---|
| Language | Python |
| App and UI | Streamlit |
| Data handling | Pandas |
| Machine learning | scikit-learn, TF-IDF, cosine similarity |
| Testing | pytest |
| Optional live movie data | TMDB API |
| Optional authentication and persistence | Supabase Auth, PostgreSQL, Row Level Security |

## 📁 Project structure

```
CINEMATCH-/
├── app.py
├── recommender.py
├── requirements.txt
├── data/
│   └── movies.csv
├── tests/
│   └── test_recommender.py
├── supabase/
│   └── schema.sql
└── scripts/
    └── import_tmdb_catalog.py
```

The optional `supabase/` and `scripts/` paths are used for the Supabase setup and TMDB catalog-import workflow described below.

## 🚀 Try the deployed app

**[Open CineMatch Live](https://cinematch-git-pyqhwbfjket6brjei4aebs.streamlit.app/)**

The application is hosted on Streamlit Community Cloud. Open the link above to explore the deployed version.

## 💻 Run locally (Windows PowerShell)

### 1. Clone the repository

```powershell
git clone https://github.com/mehulikhanra904-prog/CINEMATCH-.git
cd CINEMATCH-
```

### 2. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script activation, run this in the current terminal and activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Start the application

```powershell
python -m streamlit run app.py
```

Open **http://localhost:8501** in your browser.

## 🧪 Run tests

Run the test suite from the project root:

```powershell
python -m pytest -q
```

The tests cover recommendation behavior and error handling.

## ☁️ Deployment — Streamlit Community Cloud

The app is configured to run with Streamlit Community Cloud.

1. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) using GitHub.
2. Select **Create app** and choose the repository `mehulikhanra904-prog/CINEMATCH-`.
3. Select branch `main` and main file `app.py`.
4. Deploy the application. Dependencies are installed from `requirements.txt`.
5. Once deployment completes, use the live link at the top of this README.

## 🔐 Optional API integrations

The core app does not require secrets. To enable the optional TMDB and Supabase integrations, create your own credentials and add them under your Streamlit app's **Settings → Secrets**.

Example TOML structure (replace the placeholders with your own values):

```toml
TMDB_ACCESS_TOKEN = "your_tmdb_api_read_access_token"
SUPABASE_URL = "https://your-project-ref.supabase.co"
SUPABASE_PUBLISHABLE_KEY = "sb_publishable_your_key"
```

**Never commit real API tokens, passwords, or service-role keys to GitHub.**

### TMDB setup

1. Create or sign in to a TMDB account and open the account's API settings.
2. Request API access if required.
3. Copy the **API Read Access Token**.
4. Add it to Streamlit Secrets as `TMDB_ACCESS_TOKEN`.

This enables the optional live movie discovery and related movie metadata features. Review TMDB's API terms and attribution requirements before public or commercial use. TMDB attribution is displayed in the app.

### Supabase setup

1. Create a Supabase project.
2. In **Settings → API Keys** or the project's **Connect** dialog, copy the Project URL and **Publishable key**.
3. Open the repository's `supabase/schema.sql` in the Supabase SQL Editor and run the schema.
4. Keep email/password sign-in enabled under **Authentication → Providers → Email** if using that authentication flow.
5. Add the project URL and publishable key to Streamlit Secrets using the names shown above.

The app also accepts the legacy `SUPABASE_ANON_KEY` setting, but the publishable key is preferred. Do not expose or use a Supabase secret/service-role key in the client-facing app.

### Apply secrets

1. Open the app in the Streamlit Community Cloud dashboard.
2. Go to **Settings → Secrets** (or **Edit secrets**).
3. Add the TOML values using your real credentials and save.
4. Reboot or redeploy the app.
5. Test the enabled integration, including signing in and adding/removing a watchlist movie if Supabase is configured.

## 📚 Expanding the movie catalog

The repository includes an optional TMDB catalog import script. Back up `data/movies.csv` before running it because the script replaces that CSV.

After setting `TMDB_ACCESS_TOKEN` in your local environment, run:

```powershell
python scripts/import_tmdb_catalog.py --pages 50
```

This requests up to approximately 1,000 popular titles. Review TMDB's terms before redistributing imported data.

## 🗺️ Roadmap

- [ ] Expand the catalog with a properly licensed dataset.
- [x] Optional persistent, per-user watchlists using Supabase Auth and Row Level Security.
- [x] Optional TMDB live discovery, movie details, posters, and YouTube trailer links.
- [ ] Evaluate recommendation quality with precision, recall, or ranking metrics.
- [x] Automated tests in the project.
- [x] CI workflow to run tests on pull requests.

## 👩‍💻 Author

**Mehuli Khanra**

- GitHub: [@mehulikhanra904-prog](https://github.com/mehulikhanra904-prog)
- Project repository: [CINEMATCH-](https://github.com/mehulikhanra904-prog/CINEMATCH-)
- Live demo: [CineMatch on Streamlit](https://cinematch-git-pyqhwbfjket6brjei4aebs.streamlit.app/)

If you find CineMatch useful, consider giving the repository a ⭐.

---

*Built as a learning project to explore Python, Streamlit, and content-based movie recommendation systems.*
