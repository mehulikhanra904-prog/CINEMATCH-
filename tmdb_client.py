"""Optional TMDB API client for live movie discovery."""
import os
import requests

BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

class TMDBError(RuntimeError):
    pass

class TMDBClient:
    def __init__(self, access_token):
        if not access_token:
            raise ValueError("TMDB access token is required.")
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {access_token}", "accept": "application/json"})

    def _get(self, endpoint, params=None):
        try:
            response = self.session.get(f"{BASE_URL}/{endpoint.lstrip('/')}", params=params, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            raise TMDBError("TMDB could not be reached. Please try again later.") from exc
        except ValueError as exc:
            raise TMDBError("TMDB returned an unreadable response.") from exc

    def discover_movies(self, page=1):
        return self._get("discover/movie", {"include_adult": "false", "language": "en-US",
                                            "sort_by": "popularity.desc", "page": max(1, min(int(page), 500))})

    def search_movies(self, query, page=1):
        return self._get("search/movie", {"query": str(query).strip(), "include_adult": "false",
                                          "language": "en-US", "page": max(1, min(int(page), 500))})

    def movie_details(self, movie_id):
        return self._get(f"movie/{int(movie_id)}", {"language": "en-US", "append_to_response": "videos,credits"})

def poster_url(path):
    return f"{IMAGE_BASE}{path}" if path else None

def trailer_url(details):
    for video in details.get("videos", {}).get("results", []):
        if video.get("site") == "YouTube" and video.get("type") == "Trailer" and video.get("key"):
            return f"https://www.youtube.com/watch?v={video['key']}"
    return None
