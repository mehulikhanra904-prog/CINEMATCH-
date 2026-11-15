"""Build/refresh the local recommendation catalog from TMDB.

Usage:
  TMDB_ACCESS_TOKEN=... python scripts/import_tmdb_catalog.py --pages 10

Only import data in accordance with TMDB API terms and attribution requirements.
"""
import argparse
import os
from pathlib import Path

import pandas as pd
import requests

BASE = "https://api.themoviedb.org/3"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pages", type=int, default=5, help="Number of popular-movie pages (20 movies/page)")
    parser.add_argument("--output", default="data/movies.csv")
    args = parser.parse_args()
    token = os.getenv("TMDB_ACCESS_TOKEN")
    if not token:
        raise SystemExit("Set TMDB_ACCESS_TOKEN before running this importer.")
    headers = {"Authorization": f"Bearer {token}", "accept": "application/json"}
    session = requests.Session()
    session.headers.update(headers)
    genres = session.get(f"{BASE}/genre/movie/list", params={"language": "en"}, timeout=20)
    genres.raise_for_status()
    genre_names = {item["id"]: item["name"] for item in genres.json().get("genres", [])}
    rows = {}
    for page in range(1, max(1, min(args.pages, 500)) + 1):
        response = session.get(f"{BASE}/movie/popular", params={"language": "en-US", "page": page}, timeout=20)
        response.raise_for_status()
        for movie in response.json().get("results", []):
            movie_id = movie.get("id")
            if not movie_id:
                continue
            rows[movie_id] = {
                "title": movie.get("title", ""),
                "genres": ", ".join(genre_names.get(gid, "") for gid in movie.get("genre_ids", []) if genre_names.get(gid)),
                "overview": movie.get("overview", ""),
                "year": (movie.get("release_date") or "")[:4],
                "rating": movie.get("vote_average", ""),
                "poster_url": f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get("poster_path") else "",
            }
    frame = pd.DataFrame(rows.values(), columns=["title", "genres", "overview", "year", "rating", "poster_url"])
    if frame.empty:
        raise SystemExit("TMDB returned no movies; the existing catalog was not changed.")
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(destination, index=False)
    print(f"Wrote {len(frame)} movies to {destination}")


if __name__ == "__main__":
    main()
