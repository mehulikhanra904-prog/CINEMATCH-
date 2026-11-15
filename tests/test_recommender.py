from pathlib import Path

import pandas as pd
import pytest

from recommender import MovieRecommender


@pytest.fixture
def sample_catalog(tmp_path):
    data = pd.DataFrame([
        {"title": "Space Journey", "genres": "Sci-Fi, Adventure", "overview": "A crew explores distant planets", "year": 2020, "rating": 8.2, "poster_url": ""},
        {"title": "Planet Mission", "genres": "Sci-Fi", "overview": "Astronauts explore a new planet", "year": 2021, "rating": 7.8, "poster_url": ""},
        {"title": "Kitchen Story", "genres": "Comedy", "overview": "A chef opens a restaurant", "year": 2019, "rating": 7.1, "poster_url": ""},
    ])
    path = tmp_path / "movies.csv"
    data.to_csv(path, index=False)
    return path


def test_recommends_similar_content(sample_catalog):
    model = MovieRecommender(sample_catalog)
    result = model.recommend("Space Journey", n=2)
    assert len(result) == 2
    assert "Planet Mission" in result["title"].tolist()
    assert "Space Journey" not in result["title"].tolist()
    assert result["similarity"].between(0, 1).all()


def test_recommendation_filters(sample_catalog):
    model = MovieRecommender(sample_catalog)
    result = model.recommend("Space Journey", n=5, genre="Sci-Fi", min_rating=7.5)
    assert result["title"].tolist() == ["Planet Mission"]


def test_unknown_title_raises(sample_catalog):
    model = MovieRecommender(sample_catalog)
    with pytest.raises(ValueError, match="Movie not found"):
        model.recommend("Not a movie")


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        MovieRecommender(tmp_path / "missing.csv")


def test_free_text_vibe_search(sample_catalog):
    model = MovieRecommender(sample_catalog)
    result = model.recommend_by_query("astronauts exploring planets", n=2)
    assert len(result) == 2
    assert result.iloc[0]["title"] in {"Space Journey", "Planet Mission"}
    assert result["similarity"].between(0, 1).all()


def test_free_text_search_rejects_empty_query(sample_catalog):
    model = MovieRecommender(sample_catalog)
    with pytest.raises(ValueError, match="Please enter"):
        model.recommend_by_query("   ")
