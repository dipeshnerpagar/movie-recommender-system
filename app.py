import os
import requests
import streamlit as st
import pickle
import pandas as pd

def download_file_from_google_drive(file_id, destination):
    """
    Downloads a file from Google Drive using the file ID.
    Handles the confirmation page and downloads the actual file.
    """
    def get_confirm_token(response):
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value
        return None

    def save_response_content(response, destination):
        CHUNK_SIZE = 32768
        with open(destination, "wb") as f:
            for chunk in response.iter_content(CHUNK_SIZE):
                if chunk:
                    f.write(chunk)

    URL = "https://drive.google.com/uc?export=download"
    session = requests.Session()
    response = session.get(URL, params={'id': file_id}, stream=True)
    token = get_confirm_token(response)

    if token:
        params = {'id': file_id, 'confirm': token}
        response = session.get(URL, params=params, stream=True)

    save_response_content(response, destination)

# URLs for external hosting with file IDs
FILE_IDS = {
    'movie_dict.pkl': '1KT-hPLE2SccRDOlk60cBRlzg34NsJjkj',
    'similarity.pkl': '1jd9FlPHC_aT-CNTCKv_ZDICTrxJLzkRf'
}

@st.cache_data
def load_data():
    # Download and load files
    for filename, file_id in FILE_IDS.items():
        try:
            if not os.path.exists(filename):
                with st.spinner(f'Downloading {filename}...'):
                    download_file_from_google_drive(file_id, filename)
        except Exception as e:
            st.error(f"Error downloading {filename}: {str(e)}")
            return None, None
    
    try:
        movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
        movies = pd.DataFrame(movies_dict)
        similarity = pickle.load(open('similarity.pkl', 'rb'))
        return movies, similarity
    except Exception as e:
        st.error(f"Error loading data files: {str(e)}")
        return None, None

# Load movies and similarity matrix
movies, similarity = load_data()

if movies is None or similarity is None:
    st.error("Failed to load necessary data. Please try again later.")
    st.stop()

# Function to fetch movie poster using movie ID from TMDb API
API_KEY = 'c44a9809c74d38d6e72c7ebc8dde8d1f'
def fetch_poster(movie_id):
    response = requests.get(
        f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US'
    )
    data = response.json()
    return f"https://image.tmdb.org/t/p/w500/{data['poster_path']}"

# Function to recommend movies based on similarity
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))
    return recommended_movies, recommended_movies_posters

# Function to fetch popular or default recommended movies
def fetch_default_movies():
    default_movies = ["The Dark Knight", "Inception", "Spider-Man 3", "The Matrix", "Interstellar"]
    recommended_movies = []
    recommended_movies_posters = []

    for movie in default_movies:
        if movie in movies['title'].values:
            movie_id = movies[movies['title'] == movie].movie_id.values[0]
            recommended_movies.append(movie)
            recommended_movies_posters.append(fetch_poster(movie_id))
        else:
            st.warning(f"Movie '{movie}' not found in the dataset.")

    return recommended_movies, recommended_movies_posters

# Streamlit web app title
st.title('Movie Recommender System')

# Dropdown for movie selection with a placeholder
selected_movie_name = st.selectbox(
    'Enter Movie Name',
    options=['Choose an option'] + list(movies['title'].values),
    index=0
)

# Recommendation logic triggered by a button
if st.button('Recommend') and selected_movie_name != 'Choose an option':
    names, posters = recommend(selected_movie_name)

    cols = st.columns(5)
    for col, name, poster in zip(cols, names, posters):
        with col:
            st.text(name)
            st.image(poster)

# Display default recommendations when the page loads
if not st.session_state.get('recommendations_loaded'):
    st.session_state.recommendations_loaded = True
    default_names, default_posters = fetch_default_movies()

    cols = st.columns(5)
    for col, name, poster in zip(cols, default_names, default_posters):
        with col:
            st.text(name)
            st.image(poster)
