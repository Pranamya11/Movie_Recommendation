import streamlit as st
import requests
import pickle
import os
from dotenv import load_dotenv

load_dotenv()

movies = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

API_KEY = os.getenv("TMDB_API_KEY")


@st.cache_data
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"
    try:
        data = requests.get(url, timeout=10).json()
        poster_path = data.get("poster_path")

        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
        return "https://via.placeholder.com/300x450?text=No+Image"

    except:
        return "https://via.placeholder.com/300x450?text=Error"


def recommend(movie):
    match = movies[movies['title'] == movie]

    if match.empty:
        return [], []

    index = match.index[0]

    distances = list(enumerate(similarity[index]))
    movies_list = sorted(distances, reverse=True, key=lambda x: x[1])[1:7]

    names = []
    posters = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        names.append(movies.iloc[i[0]].title)
        posters.append(fetch_poster(movie_id))

    return names, posters


st.set_page_config(page_title="Movie Recommender", layout="wide")


st.markdown("""
<style>
.main { background-color: #0E1117; }

.title {
    text-align: center;
    font-size: 40px;
    color: #E50914;
    font-weight: bold;
    margin-bottom: 20px;
}

.movie-card { text-align: center; padding: 5px; }

.small-img img { border-radius: 10px; height: 280px; }
</style>
""", unsafe_allow_html=True)


st.markdown("<div class='title'>🎬 Movie Recommender</div>", unsafe_allow_html=True)

left, right = st.columns([1, 2])

# ================= LEFT =================
with left:
    st.markdown("## 🔍 Search Movie")

    selected_movie = st.selectbox(
        "Choose a movie",
        movies['title'].values
    )

    st.markdown("### 🎥 Selected Movie")

    movie_id = movies[movies['title'] == selected_movie].iloc[0].movie_id
    poster_url = fetch_poster(movie_id)

    st.image(poster_url, use_container_width=True)
    st.caption(selected_movie)


# ================= RIGHT =================
with right:
    st.markdown("## 🎯 Recommendations")

    # 🔥 AUTO UPDATE (no button needed)
    names, posters = recommend(selected_movie)

    cols = st.columns(3)

    for i in range(len(names)):
        with cols[i % 3]:
            st.image(posters[i], use_container_width=True)
            st.markdown(
                f"<div style='text-align:center;font-size:14px'>{names[i]}</div>",
                unsafe_allow_html=True
            )