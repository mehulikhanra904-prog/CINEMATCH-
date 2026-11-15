# 🎬 CineMatch — Movie Discovery & Recommendation

A clean, dark-themed movie discovery app with a content-based recommendation engine. Search the catalog, filter by genre, sort films, save a session watchlist, and discover movies similar to a favorite.

> **Demo catalog:** `data/movies.csv` is a small curated sample. Recommendations are content-based—not collaborative recommendations from user behavior.

## ✨ Features
- Search movie titles, genres, and plot descriptions
- Filter by genre; sort by rating, release year, or title
- Movie cards with poster, genre, year, and rating (fallback when poster is missing)
- Content-based recommendations with similarity percentages
- Optional genre and minimum-rating filters for recommendations
- Session watchlist (saved while the current Streamlit session remains active)
- Responsive Streamlit layout and friendly empty/error states
- Unit tests for recommendation behavior and error handling

## 🧠 How recommendations work
1. Combine each movie's genres and overview into a text feature.
2. Convert text to TF-IDF vectors, including unigram and bigram features.
3. Compare vectors using cosine similarity.
4. Rank candidates and apply optional genre/rating filters.

This is an explainable beginner-friendly ML baseline. Similarity scores measure textual similarity, **not** the probability that you will like a film.

## 🧰 Tech stack
Python · Streamlit · Pandas · scikit-learn · pytest

## 📁 Project structure
```
CINEMATCH-/
├── app.py
├── recommender.py
├── requirements.txt
├── data/
│   └── movies.csv
└── tests/
    └── test_recommender.py
```

## ▶️ Run locally (Windows PowerShell)
```powershell
git clone https://github.com/mehulikhanra904-prog/CINEMATCH-.git
cd CINEMATCH-
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run app.py
```
Open **http://localhost:8501**.

If PowerShell blocks activation, run this in the current terminal:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## 🧪 Run tests
```powershell
python -m pytest -q
```

## ☁️ Deploy on Streamlit Community Cloud
1. Open [Streamlit Community Cloud](https://share.streamlit.io/) and sign in with GitHub.
2. Choose **Create app** → **Deploy a public app from GitHub**.
3. Repository: `mehulikhanra904-prog/CINEMATCH-`
4. Branch: `main` · Main file: `app.py`
5. Click **Deploy**. Streamlit installs dependencies from `requirements.txt`.
6. Copy the app URL shown after the build finishes and add it to this README.

The core app needs no secrets. Optional live TMDB discovery requires TMDB_ACCESS_TOKEN in Streamlit Secrets. Add it as `TMDB_ACCESS_TOKEN = "your_read_access_token"`. Never commit API credentials. TMDB attribution is shown in the app; review the TMDB API terms and attribution requirements before public or commercial use.

To expand the local ML catalog, set `TMDB_ACCESS_TOKEN` in your terminal and run `python scripts/import_tmdb_catalog.py --pages 50` (up to roughly 1,000 popular titles). Back up `data/movies.csv` first; the script replaces that CSV with the downloaded catalog. Review TMDB's terms before redistributing imported data.

## 🗺️ Roadmap
- [ ] Expand catalog using a properly licensed dataset
- [x] Optional persistent, per-user watchlists using Supabase Auth and Row Level Security
- [x] Optional TMDB live discovery, movie details, posters, and YouTube trailer links (requires API read access token)
- [ ] Evaluate recommendations with precision/recall or ranking metrics
- [ ] Add CI to run tests on each pull request

## 👩‍💻 Author
**Mehuli Khanra** · [GitHub](https://github.com/mehulikhanra904-prog)

If you find this useful, consider starring the repository ⭐
