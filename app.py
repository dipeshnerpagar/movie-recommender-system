```python
import os
import requests
import streamlit as st
import pickle
import pandas as pd

# Google Drive download helper (handles large file warnings)
def download_from_google_drive(file_id, destination):
    """
    Downloads a file from Google Drive given its file ID, handling confirmation tokens for large files.
    """
    URL = "https://docs.google.com/uc?export=download"
    session = requests.Session()
    # Initial request
    response = session.get(URL, params={'id': file_id}, stream=True)
    # Check for confirmation token
    token = None
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            token = value
    if token:
        # Re-request with confirmation token
        response = session.get(URL, params={'id': file_id, 'confirm': token}, stream=True)
    # Save file
    with open(destination, 'wb') as f:
        for chunk in response.iter_content(32768):
            if chunk:
                f.write(chunk)

# Mapping of files to their Google Drive file IDs
FILE_IDS = {
    'movie_dict.pkl': 'https://drive.google.com/uc?export=download&id=1KT-hPLE2SccRDOlk60cBRlzg34NsJjkj',
    'similarity.pkl': 'https://drive.google.com/uc?export=download&id=1jd9FlPHC_aT-CNTCKv_ZDICTrxJLzkRf'
}

# Download files if not already present
for filename, file_id in FILE_IDS.items():
    if not os.path.exists(filename):
        download_from_google_drive(file_id, filename)

# Load movies and similarity matrix
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# TMDb API Key
API_KEY = 'c44a9809c74d38d6e72c7ebc8dde8d1f'

# Function to fetch movie poster using movie ID
def fetch_poster(movie_id):
    response = requests.get(
        f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US'
    )
    data = response.json()
    return f"https://image.tmdb.org/t/p/w500/{data['poster_path']}"

# Recommend movies based on similarity
def recommend(movie):
    idx = movies[movies['title'] == movie].index[0]
    distances = similarity[idx]
    top5 = sorted(enumerate(distances), key=lambda x: x[1], reverse=True)[1:6]

    names, posters = [], []
    for i, _ in top5:
        movie_id = movies.iloc[i].movie_id
        names.append(movies.iloc[i].title)
        posters.append(fetch_poster(movie_id))
    return names, posters

# Fetch default recommendations
def fetch_default_movies():
    defaults = ["The Dark Knight", "Inception", "Spider-Man 3", "The Matrix", "Interstellar"]
    names, posters = [], []
    for movie in defaults:
        if movie in movies['title'].values:
            mid = movies[movies['title'] == movie].movie_id.values[0]
            names.append(movie)
            posters.append(fetch_poster(mid))
        else:
            st.warning(f"Movie '{movie}' not found in dataset.")
    return names, posters

# Streamlit app
st.title('Movie Recommender System')

selected = st.selectbox(
    'Enter Movie Name',
    ['Choose an option'] + list(movies['title'].values),
    index=0
)

if st.button('Recommend') and selected != 'Choose an option':
    names, posters = recommend(selected)
    cols = st.columns(5)
    for col, name, poster in zip(cols, names, posters):
        with col:
            st.text(name)
            st.image(poster)

# Default recommendations on first load
if not st.session_state.get('loaded'):
    st.session_state['loaded'] = True
    names, posters = fetch_default_movies()
    cols = st.columns(5)
    for col, name, poster in zip(cols, names, posters):
        with col:
            st.text(name)
            st.image(poster)
```
