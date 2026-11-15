from pathlib import Path
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class MovieRecommender:
    def __init__(self, csv_path="data/movies.csv"):
        path=Path(csv_path)
        if not path.exists(): raise FileNotFoundError(f"Dataset not found: {path}")
        self.movies=pd.read_csv(path).fillna("")
        required={"title","genres","overview","year","rating","poster_url"}
        if not required.issubset(self.movies.columns): raise ValueError(f"CSV requires: {required}")
        self.movies["features"]=self.movies["genres"].astype(str)+" "+self.movies["overview"].astype(str)
        self.vectorizer=TfidfVectorizer(stop_words="english")
        self.matrix=self.vectorizer.fit_transform(self.movies["features"])
        self.similarity=cosine_similarity(self.matrix)
        self.indices={str(title):i for i,title in enumerate(self.movies["title"])}
    def recommend(self,title,n=5):
        if title not in self.indices: raise ValueError(f"Movie not found: {title}")
        idx=self.indices[title]
        ranked=sorted(enumerate(self.similarity[idx]),key=lambda x:x[1],reverse=True)
        ranked=[(i,s) for i,s in ranked if i!=idx][:n]
        result=self.movies.iloc[[i for i,_ in ranked].copy()].copy()
        result["similarity"]=[float(s) for _,s in ranked]
        return result.reset_index(drop=True)
