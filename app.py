import html

import pandas as pd
import streamlit as st
from recommender import MovieRecommender

st.set_page_config(page_title="CineMatch | Discover films", page_icon="🎬", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html,body,[class*="css"]{font-family:Inter,sans-serif}
.stApp{background:#080a12;color:#f5f6ff}
.block-container{max-width:1500px;padding-top:1.5rem}
.hero{padding:42px;border-radius:24px;background:linear-gradient(115deg,#20194a,#11182d 55%,#10121d);border:1px solid #302b55;margin-bottom:24px}
.hero h1{font-size:3.25rem;font-weight:800;letter-spacing:-2px;margin:0}
.hero p{color:#b9bdd5;font-size:1.05rem;margin:8px 0 0}
.section-title{font-size:1.55rem;font-weight:750;margin:22px 0 12px}
.poster{height:250px;border-radius:14px;background:linear-gradient(145deg,#27234e,#111725 70%);display:flex;align-items:center;justify-content:center;text-align:center;padding:16px;color:#c5baff;font-size:1.15rem;font-weight:800;border:1px solid #34324d;overflow:hidden}
.poster img{width:100%;height:250px;object-fit:cover}
.card{background:#121522;border:1px solid #292c40;border-radius:16px;padding:14px;margin-top:9px;min-height:150px}
.card h4{margin:0 0 8px;font-size:1rem;color:#fff}
.muted{color:#a9aec8;font-size:.84rem}
.rating{color:#ffd166;font-weight:700}
.stButton>button{background:linear-gradient(90deg,#7657f5,#4b8dff);color:#fff;border:0;border-radius:10px;font-weight:700}
div[data-baseweb="select"]>div{background:#151827;border-color:#33364e}
div[data-testid="stMetric"]{background:#121522;border:1px solid #292c40;padding:14px;border-radius:14px}
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_model():
    return MovieRecommender("data/movies.csv")


try:
    model = load_model()
except Exception as exc:
    st.error(f"Could not load movie catalog: {exc}")
    st.stop()

df = model.movies.copy()
st.session_state.setdefault("watchlist", [])

# Optional persistent watchlist with per-user Supabase authentication.
from watchlist_store import configured as watchlist_configured
watchlist_user = None
if watchlist_configured():
    from watchlist_store import restore_session, sign_in, sign_up, save_session, load_watchlist
    with st.sidebar:
        st.subheader("🔐 Your account")
        try:
            watchlist_user = restore_session()
        except Exception:
            st.session_state.pop("supabase_session", None)
            watchlist_user = None
        if watchlist_user:
            st.success(f"Signed in: {watchlist_user.email}")
            if st.button("Sign out", key="watchlist_signout"):
                st.session_state.pop("supabase_session", None)
                st.session_state.pop("supabase_client", None)
                st.rerun()
            try:
                st.session_state.watchlist = load_watchlist(str(watchlist_user.id))
            except Exception as exc:
                st.warning(f"Could not load your saved watchlist: {exc}")
        else:
            auth_mode = st.radio("Account action", ["Sign in", "Create account"], horizontal=True)
            with st.form("watchlist_auth_form"):
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                auth_submit = st.form_submit_button(auth_mode)
            if auth_submit:
                try:
                    response = sign_in(email, password) if auth_mode == "Sign in" else sign_up(email, password)
                    if response.session:
                        save_session(response.session)
                        st.success("Account ready. Your watchlist is synced.")
                        st.rerun()
                    else:
                        st.info("Check your email to confirm your account, then sign in.")
                except Exception as exc:
                    st.error(f"Authentication failed: {exc}")


st.markdown(
    '<div class="hero"><h1>🎬 CineMatch</h1><p>Your next favorite film is one search away · Discover, compare, save.</p></div>',
    unsafe_allow_html=True,
)

m1, m2, m3 = st.columns(3)
m1.metric("🎞️ Movies", len(df))
ratings = pd.to_numeric(df["rating"], errors="coerce")
m2.metric("⭐ Average rating", f"{ratings.mean():.1f}/10" if ratings.notna().any() else "N/A")
m3.metric("🧠 Recommendation engine", "TF-IDF · cosine")

st.markdown('<div class="section-title">🔎 Explore the collection</div>', unsafe_allow_html=True)
search = st.text_input("Search", placeholder="Title, genre, or plot keyword…")
genres = sorted({g.strip() for row in df["genres"] for g in str(row).split(",") if g.strip()})
filters = st.columns([2, 1, 1])
with filters[0]:
    genre = st.selectbox("Genre", ["All genres"] + genres)
with filters[1]:
    sort = st.selectbox("Sort by", ["Top rated", "Newest", "A–Z"])
with filters[2]:
    watch_only = st.checkbox("Watchlist only")

filtered = df.copy()
if search:
    mask = filtered.apply(
        lambda row: search.casefold() in (
            str(row["title"]) + " " + str(row["genres"]) + " " + str(row["overview"])
        ).casefold(),
        axis=1,
    )
    filtered = filtered[mask]
if genre != "All genres":
    filtered = filtered[filtered["genres"].str.contains(genre, case=False, na=False)]
if watch_only:
    filtered = filtered[filtered["title"].isin(st.session_state.watchlist)]
if sort == "Top rated":
    filtered = filtered.assign(_rating=pd.to_numeric(filtered["rating"], errors="coerce")).sort_values("_rating", ascending=False)
elif sort == "Newest":
    filtered = filtered.assign(_year=pd.to_numeric(filtered["year"], errors="coerce")).sort_values("_year", ascending=False)
else:
    filtered = filtered.sort_values("title")

st.caption(f"Showing {len(filtered)} of {len(df)} movies")
if filtered.empty:
    st.info("No movies match these filters. Try another search or genre.")
else:
    cols = st.columns(5)
    for i, (_, movie) in enumerate(filtered.iterrows()):
        with cols[i % 5]:
            poster = str(movie.get("poster_url", "")).strip()
            title = str(movie["title"])
            if poster.startswith("https://") or poster.startswith("http://"):
                st.image(poster, use_container_width=True)
            else:
                st.markdown(f'<div class="poster">🍿<br>{html.escape(title)}</div>', unsafe_allow_html=True)
            rating = pd.to_numeric(movie["rating"], errors="coerce")
            rating_text = f"⭐ {rating:.1f}/10" if pd.notna(rating) else "⭐ Not rated"
            st.markdown(
                f'<div class="card"><h4>{html.escape(title)}</h4><div class="muted">{html.escape(str(movie["year"]))} · {html.escape(str(movie["genres"]))}</div><p class="rating">{rating_text}</p></div>',
                unsafe_allow_html=True,
            )
            saved = title in st.session_state.watchlist
            if st.button("✓ Saved" if saved else "＋ Watchlist", key=f"watch_{i}_{title}", use_container_width=True):
                if saved:
                    st.session_state.watchlist.remove(title)
                    if watchlist_user:
                        from watchlist_store import remove_movie
                        remove_movie(str(watchlist_user.id), title)
                else:
                    st.session_state.watchlist.append(title)
                    if watchlist_user:
                        from watchlist_store import add_movie
                        add_movie(str(watchlist_user.id), title)
                st.rerun()

st.markdown("---")
st.markdown('<div class="section-title">✨ Find films like your favorites</div>', unsafe_allow_html=True)
left, right = st.columns([3, 1])
with left:
    chosen = st.selectbox("Pick a movie", df["title"].tolist(), key="recommend_select")
with right:
    count = st.selectbox("Number of picks", [3, 5, 8, 10], index=1)
rec_genres = st.multiselect("Optional genre filter", genres, help="Leave empty to see all similar genres.")
min_rating = st.slider("Minimum rating", 0.0, 10.0, 0.0, 0.5)

if st.button("✨ Recommend movies", use_container_width=True):
    genre_filter = rec_genres[0] if len(rec_genres) == 1 else None
    recommendations = model.recommend(chosen, n=len(df), genre=genre_filter, min_rating=min_rating)
    if len(rec_genres) > 1:
        recommendations = recommendations[recommendations["genres"].apply(
            lambda value: any(g.casefold() in str(value).casefold() for g in rec_genres)
        )]
    recommendations = recommendations.head(count)
    if recommendations.empty:
        st.warning("No matches with these filters. Lower the rating threshold or remove genre filters.")
    else:
        st.success(f"Recommended because you liked **{chosen}**")
        cards = st.columns(min(5, len(recommendations)))
        for j, (_, movie) in enumerate(recommendations.iterrows()):
            with cards[j % len(cards)]:
                poster = str(movie.get("poster_url", "")).strip()
                if poster.startswith(("https://", "http://")):
                    st.image(poster, use_container_width=True)
                else:
                    st.markdown(f'<div class="poster">🎞️<br>{html.escape(str(movie["title"]))}</div>', unsafe_allow_html=True)
                rating = pd.to_numeric(movie["rating"], errors="coerce")
                rating_text = f"⭐ {rating:.1f}/10" if pd.notna(rating) else "⭐ Not rated"
                st.markdown(
                    f'<div class="card"><h4>{html.escape(str(movie["title"]))}</h4><div class="muted">{html.escape(str(movie["year"]))} · {html.escape(str(movie["genres"]))}</div><p class="rating">{rating_text}</p><div class="muted">Similarity: {float(movie["similarity"]):.0%}</div></div>',
                    unsafe_allow_html=True,
                )


st.markdown('<div class="section-title">💭 Discover by mood or story</div>', unsafe_allow_html=True)
st.caption("Describe what you feel like watching — no movie title required.")
vibe_query = st.text_input(
    "What are you in the mood for?",
    placeholder="e.g. mind-bending sci-fi, emotional love story, funny family adventure…",
    key="vibe_query",
)
vibe_cols = st.columns([1, 3])
with vibe_cols[0]:
    vibe_count = st.selectbox("Vibe results", [3, 5, 8], index=1, key="vibe_count")
with vibe_cols[1]:
    st.write("")
    st.write("")
    vibe_submit = st.button("Find my movie 🍿", key="vibe_submit")
if vibe_submit:
    if not vibe_query.strip():
        st.warning("Describe a mood, theme, or story first.")
    else:
        vibe_results = model.recommend_by_query(vibe_query, n=vibe_count)
        if vibe_results.empty or float(vibe_results["similarity"].max()) <= 0:
            st.info("I couldn't find a strong match. Try describing a genre, theme, or plot in different words.")
        else:
            st.success("Here are the closest matches from the current catalog.")
            vibe_cards = st.columns(min(5, len(vibe_results)))
            for k, (_, movie) in enumerate(vibe_results.iterrows()):
                with vibe_cards[k % len(vibe_cards)]:
                    poster = str(movie.get("poster_url", "")).strip()
                    if poster.startswith(("https://", "http://")):
                        st.image(poster, use_container_width=True)
                    else:
                        st.markdown(f'<div class="poster">🍿<br>{html.escape(str(movie["title"]))}</div>', unsafe_allow_html=True)
                    rating = pd.to_numeric(movie["rating"], errors="coerce")
                    rating_text = f"⭐ {rating:.1f}/10" if pd.notna(rating) else "⭐ Not rated"
                    st.markdown(
                        f'<div class="card"><h4>{html.escape(str(movie["title"]))}</h4><div class="muted">{html.escape(str(movie["year"]))} · {html.escape(str(movie["genres"]))}</div><p class="rating">{rating_text}</p><div class="muted">Text match: {float(movie["similarity"]):.0%}</div></div>',
                        unsafe_allow_html=True,
                    )


# Optional live catalog powered by TMDB. Existing features work without a key.
st.markdown("---")
st.markdown('<div class="section-title">🌍 Explore the live movie universe</div>', unsafe_allow_html=True)
st.caption("Browse popular movies from The Movie Database (TMDB), search titles, and open movie details and trailers.")
try:
    tmdb_token = st.secrets.get("TMDB_ACCESS_TOKEN", None)
except Exception:
    tmdb_token = None
if not tmdb_token:
    import os
    tmdb_token = os.getenv("TMDB_ACCESS_TOKEN")

if not tmdb_token:
    st.info("Live discovery is optional. Add TMDB_ACCESS_TOKEN to Streamlit Secrets to enable the live catalog. Existing CineMatch features continue to work without it.")
else:
    from tmdb_client import TMDBClient, TMDBError, poster_url, trailer_url
    @st.cache_resource
    def get_tmdb_client(token):
        return TMDBClient(token)
    tmdb = get_tmdb_client(tmdb_token)
    live_query = st.text_input("Search the live TMDB catalog", placeholder="Search for a movie title…", key="tmdb_query")
    live_page = st.number_input("Catalog page", min_value=1, max_value=500, value=1, step=1, key="tmdb_page")
    try:
        live_data = tmdb.search_movies(live_query, live_page) if live_query.strip() else tmdb.discover_movies(live_page)
        live_movies = live_data.get("results", [])
        st.caption(f"Page {live_data.get('page', live_page)} · {live_data.get('total_results', 0):,} matching movies")
        if not live_movies:
            st.info("No live catalog matches. Try a different title.")
        else:
            live_cols = st.columns(5)
            for index, item in enumerate(live_movies[:20]):
                with live_cols[index % 5]:
                    image_url = poster_url(item.get("poster_path"))
                    if image_url:
                        st.image(image_url, use_container_width=True)
                    else:
                        st.markdown(f'<div class="poster">🎬<br>{html.escape(item.get("title", "Untitled"))}</div>', unsafe_allow_html=True)
                    title = item.get("title", "Untitled")
                    release = (item.get("release_date") or "Release date unavailable")[:4]
                    vote = item.get("vote_average")
                    vote_text = f"{float(vote):.1f}/10" if vote else "Not rated"
                    st.markdown(f'<div class="card"><h4>{html.escape(title)}</h4><div class="muted">{release}</div><p class="rating">⭐ {vote_text}</p></div>', unsafe_allow_html=True)
                    if st.button("Movie details", key=f"tmdb_details_{item['id']}", use_container_width=True):
                        st.session_state["tmdb_selected_id"] = int(item["id"])
        if st.session_state.get("tmdb_selected_id"):
            details = tmdb.movie_details(st.session_state["tmdb_selected_id"])
            st.markdown("### " + html.escape(details.get("title", "Movie details")))
            detail_cols = st.columns([1, 2])
            with detail_cols[0]:
                detail_poster = poster_url(details.get("poster_path"))
                if detail_poster:
                    st.image(detail_poster, use_container_width=True)
            with detail_cols[1]:
                st.write(details.get("overview") or "No overview available.")
                st.write(f"**Release:** {details.get('release_date') or 'N/A'}")
                st.write(f"**Genres:** {', '.join(g['name'] for g in details.get('genres', [])) or 'N/A'}")
                st.write(f"**Runtime:** {details.get('runtime') or 'N/A'} minutes")
                trailer = trailer_url(details)
                if trailer:
                    st.link_button("▶ Watch trailer on YouTube", trailer)
                else:
                    st.caption("No YouTube trailer is currently listed for this title.")
                st.link_button("View on TMDB", f"https://www.themoviedb.org/movie/{details['id']}")
    except TMDBError as exc:
        st.warning(str(exc))
    except Exception as exc:
        st.warning(f"Live movie details are temporarily unavailable: {exc}")

with st.expander("TMDB credits and attribution"):
    st.write("This product uses the TMDB API but is not endorsed or certified by TMDB. Movie metadata and images are provided by The Movie Database.")
    st.link_button("The Movie Database", "https://www.themoviedb.org/")

with st.expander("📚 How CineMatch works"):
    st.write(
        "Genres and plot summaries are cleaned and converted into TF-IDF features (including two-word phrases). "
        "Cosine similarity ranks movies by how close their content is to your selected film. "
        "You can also describe a mood or plot and rank films against that text. Watchlist is stored in this browser session; it is not an account or permanent database."
    )
st.caption("CineMatch · Python · Pandas · Scikit-learn · Streamlit")
