# 🎬 CineMatch — Movie Discovery & Recommendation System

A portfolio-ready starter app with a modern dark discovery interface, movie search, genre filtering, sorting, ratings, release years, poster URLs, and content-based recommendations.

## Features
- Premium dark UI inspired by streaming catalogs (not affiliated with Netflix)
- Movie catalog cards with poster images (when URL is available), year, genre, and rating
- Search across titles, genres, and descriptions
- Genre filter + Top rated / Newest / A–Z sorting
- Content-based recommendations using TF-IDF + cosine similarity
- Similarity score for each recommendation

## Stack
Python • Streamlit • Pandas • Scikit-learn

## Setup (Windows PowerShell)
```powershell
cd "C:\path\to\CineMatch_Complete"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```
Open http://localhost:8501

## Dataset
`data/movies.csv` is a small curated demo dataset. It includes title, genres, overview, year, rating, and poster_url. A few poster URLs are supplied as examples; blank poster URLs render a styled fallback. For a larger dataset, use a properly licensed source and verify image URLs/metadata.

## GitHub
```bash
git init
git add .
git commit -m "Build CineMatch movie discovery and recommendation app"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/cinematch.git
git push -u origin main
```

## Possible next features
- TMDB API integration (API key and terms required)
- Watchlist / favorites
- User accounts
- Recommendation evaluation and unit tests
- Deploy to Streamlit Community Cloud
