"""Supabase-backed, authenticated watchlist storage for CineMatch."""
import streamlit as st
from supabase import Client, create_client

def configured():
    return bool(st.secrets.get("SUPABASE_URL") and st.secrets.get("SUPABASE_ANON_KEY"))

def client() -> Client:
    if "supabase_client" not in st.session_state:
        st.session_state.supabase_client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_ANON_KEY"])
    return st.session_state.supabase_client

def sign_in(email: str, password: str):
    return client().auth.sign_in_with_password({"email": email, "password": password})

def sign_up(email: str, password: str):
    return client().auth.sign_up({"email": email, "password": password})

def restore_session():
    session = st.session_state.get("supabase_session")
    if not session:
        return None
    client().auth.set_session(session["access_token"], session["refresh_token"])
    return client().auth.get_user().user

def save_session(session):
    st.session_state.supabase_session = {"access_token": session.access_token, "refresh_token": session.refresh_token}

def load_watchlist(user_id: str):
    response = client().table("watchlist").select("movie_title").eq("user_id", user_id).order("created_at").execute()
    return [row["movie_title"] for row in response.data]

def add_movie(user_id: str, title: str):
    client().table("watchlist").upsert({"user_id": user_id, "movie_title": title}, on_conflict="user_id,movie_title").execute()

def remove_movie(user_id: str, title: str):
    client().table("watchlist").delete().eq("user_id", user_id).eq("movie_title", title).execute()
