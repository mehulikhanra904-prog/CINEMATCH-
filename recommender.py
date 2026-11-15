from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class MovieRecommender:
    """Content-based movie recommender using genres and plot summaries."""

    REQUIRED_COLUMNS = {"title", "genres", "overview", "year", "rating", "poster_url"}

    def __init__(self, csv_path="data/movies.csv"):
        path = Path(csv_path)
        if not path.exists():
            raise FileNotFoundError(f"Dataset not found: {path}")

        self.movies = pd.read_csv(path).fillna("")
        missing = self.REQUIRED_COLUMNS - set(self.movies.columns)
        if missing:
            raise ValueError(f"CSV is missing required columns: {sorted(missing)}")

        self.movies["title"] = self.movies["title"].astype(str).str.strip()
        self.movies = self.movies[self.movies["title"] != ""].drop_duplicates("title").reset_index(drop=True)
        self.movies["genres"] = self.movies["genres"].astype(str)
        self.movies["overview"] = self.movies["overview"].astype(str)
        # Give genre terms a little extra influence in the similarity model.
        self.movies["features"] = (
            self.movies["genres"].str.replace(",", " ", regex=False) + " "
            + self.movies["genres"].str.replace(",", " ", regex=False) + " "
            + self.movies["overview"]
        )

        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=1)
        self.matrix = self.vectorizer.fit_transform(self.movies["features"])
        self.similarity = cosine_similarity(self.matrix)
        self.indices = {title: i for i, title in enumerate(self.movies["title"])}

    def _filter_and_rank(self, candidates, n, genre=None, min_rating=None):
        if genre:
            candidates = candidates[candidates["genres"].str.contains(genre, case=False, na=False)]
        if min_rating is not None:
            ratings = pd.to_numeric(candidates["rating"], errors="coerce")
            candidates = candidates[ratings >= float(min_rating)]
        return candidates.head(max(0, int(n))).reset_index(drop=True)

    def recommend(self, title, n=5, genre=None, min_rating=None):
        """Return movies similar to a catalog title, with optional filters."""
        if title not in self.indices:
            raise ValueError(f"Movie not found: {title}")
        idx = self.indices[title]
        ranked = sorted(enumerate(self.similarity[idx]), key=lambda item: item[1], reverse=True)
        ranked = [(i, score) for i, score in ranked if i != idx]
        candidates = self.movies.iloc[[i for i, _ in ranked]].copy()
        candidates["similarity"] = [float(score) for _, score in ranked]
        return self._filter_and_rank(candidates, n, genre, min_rating)

    def recommend_by_query(self, query, n=5, genre=None, min_rating=None):
        """Find catalog movies matching a free-text mood, theme, or plot request."""
        query = str(query).strip()
        if not query:
            raise ValueError("Please enter a mood, theme, or description.")
        query_vector = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vector, self.matrix).ravel()
        ranked = sorted(enumerate(scores), key=lambda item: item[1], reverse=True)
        candidates = self.movies.iloc[[i for i, _ in ranked]].copy()
        candidates["similarity"] = [float(score) for _, score in ranked]
        return self._filter_and_rank(candidates, n, genre, min_rating)
