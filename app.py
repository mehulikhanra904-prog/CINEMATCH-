import streamlit as st
import pandas as pd
from recommender import MovieRecommender

st.set_page_config(page_title="CineMatch • Movie Discovery",page_icon="🎬",layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html,body,[class*="css"]{font-family:Inter,sans-serif}
.stApp{background:#080a12;color:#f5f6ff}
.block-container{max-width:1450px;padding-top:1.6rem}
.hero{padding:38px 42px;border-radius:24px;background:linear-gradient(115deg,#20194a 0%,#11182d 55%,#10121d 100%);border:1px solid #302b55;margin-bottom:25px}
.hero h1{font-size:3.2rem;font-weight:800;letter-spacing:-2px;margin:0}
.hero p{color:#b9bdd5;font-size:1.05rem;margin:8px 0 0}
.section-title{font-size:1.55rem;font-weight:750;margin:22px 0 12px}
.poster{height:260px;border-radius:14px;background:linear-gradient(145deg,#27234e,#111725 70%);display:flex;align-items:center;justify-content:center;text-align:center;padding:16px;color:#c5baff;font-size:1.25rem;font-weight:800;border:1px solid #34324d;overflow:hidden}
.poster img{width:100%;height:260px;object-fit:cover}
.card{background:#121522;border:1px solid #292c40;border-radius:16px;padding:14px;margin-top:9px;min-height:135px}
.card h4{margin:0 0 8px;font-size:1rem;color:#fff}
.muted{color:#a9aec8;font-size:.84rem}
.rating{color:#ffd166;font-weight:700}
.stButton>button{background:linear-gradient(90deg,#7657f5,#4b8dff);color:#fff;border:0;border-radius:10px;font-weight:700}
div[data-baseweb="select"]>div{background:#151827;border-color:#33364e}
div[data-testid="stMetric"]{background:#121522;border:1px solid #292c40;padding:14px;border-radius:14px}
</style>
""",unsafe_allow_html=True)

@st.cache_resource
def load_model(): return MovieRecommender("data/movies.csv")
try: model=load_model()
except Exception as e: st.error(f"Dataset error: {e}");st.stop()
df=model.movies.copy()
st.markdown('<div class="hero"><h1>🎬 CineMatch</h1><p>Find your next obsession. Curated discovery powered by content-based machine learning.</p></div>',unsafe_allow_html=True)

a,b,c=st.columns(3)
a.metric("🎞️ Titles",len(df))
b.metric("⭐ Average rating",f"{pd.to_numeric(df.rating,errors='coerce').mean():.1f}/10")
c.metric("🧠 Engine","TF-IDF + cosine")

st.markdown('<div class="section-title">🔥 Explore the collection</div>',unsafe_allow_html=True)
search=st.text_input("Search movies or genres",placeholder="Search a title, genre, or keyword…")
genres=sorted({g.strip() for row in df.genres for g in str(row).split(",") if g.strip()})
genre=st.selectbox("Filter by genre",["All genres"]+genres)
filtered=df.copy()
if search:
    filtered=filtered[filtered.apply(lambda r:search.lower() in (str(r.title)+" "+str(r.genres)+" "+str(r.overview)).lower(),axis=1)]
if genre!="All genres": filtered=filtered[filtered.genres.str.contains(genre,case=False,na=False)]
sort=st.selectbox("Sort collection",["Top rated","Newest","A–Z"])
if sort=="Top rated": filtered=filtered.sort_values("rating",ascending=False)
elif sort=="Newest": filtered=filtered.sort_values("year",ascending=False)
else: filtered=filtered.sort_values("title")
st.caption(f"{len(filtered)} titles")
cols=st.columns(5)
for i,(_,m) in enumerate(filtered.iterrows()):
    with cols[i%5]:
        poster=str(m.poster_url).strip()
        if poster and poster.startswith("http"):
            st.markdown(f'<div class="poster"><img src="{poster}"/></div>',unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="poster">🎥<br>{m.title}</div>',unsafe_allow_html=True)
        st.markdown(f'<div class="card"><h4>{m.title}</h4><div class="muted">{m.year} • {m.genres}</div><p class="rating">⭐ {float(m.rating):.1f}/10</p></div>',unsafe_allow_html=True)

st.markdown("---")
st.markdown('<div class="section-title">✨ Personalized similar-movie picks</div>',unsafe_allow_html=True)
x,y=st.columns([3,1])
with x: chosen=st.selectbox("Choose a movie you enjoyed",df.title.tolist(),key="recommend_select")
with y: num=st.selectbox("Recommendations",[3,5,8,10],index=1)
if st.button("✨ Recommend similar movies",use_container_width=True):
    recs=model.recommend(chosen,n=num)
    st.success(f"Because you liked **{chosen}**")
    cc=st.columns(min(5,len(recs)))
    for j,(_,m) in enumerate(recs.iterrows()):
        with cc[j%len(cc)]:
            p=str(m.poster_url).strip()
            if p.startswith("http"): st.markdown(f'<div class="poster"><img src="{p}"/></div>',unsafe_allow_html=True)
            else: st.markdown(f'<div class="poster">🍿<br>{m.title}</div>',unsafe_allow_html=True)
            st.markdown(f'<div class="card"><h4>{m.title}</h4><div class="muted">{m.year} • {m.genres}</div><p class="rating">⭐ {float(m.rating):.1f}/10</p><div class="muted">Match: {float(m.similarity):.0%}</div></div>',unsafe_allow_html=True)
with st.expander("📖 How CineMatch works"):
    st.write("Movie genres and plot summaries are transformed into TF-IDF vectors. Cosine similarity compares each movie with the selected title and ranks the closest matches. Ratings and release years are catalog metadata.")
st.caption("CineMatch • Python · Pandas · Scikit-learn · Streamlit")
