import streamlit as st
import pickle
import pandas as pd
import requests


# Function to fetch movie poster using movie ID from TMDb API
def fetch_poster(movie_id):
    response = requests.get(
        'https://api.themoviedb.org/3/movie/{}?api_key=c44a9809c74d38d6e72c7ebc8dde8d1f&language=en-US'.format(
            movie_id))
    data = response.json()
    return "https://image.tmdb.org/t/p/w500/" + data['poster_path']


# Function to recommend movies based on similarity
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        # Fetch poster for the recommended movie
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
            st.warning(f"Movie '{movie}' not found in the dataset.")  # Optional: Display a warning message

    return recommended_movies, recommended_movies_posters


# Load movies and similarity matrix
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Streamlit web app title
st.title('Movie Recommender System')

# Dropdown for movie selection with a placeholder
selected_movie_name = st.selectbox(
    'Enter Movie Name',
    options=['Choose an option'] + list(movies['title'].values),  # Adding placeholder option
    index=0  # Ensures that 'Choose an option' is displayed first
)

# Recommendation logic triggered by a button
if st.button('Recommend') and selected_movie_name != 'Choose an option':
    names, posters = recommend(selected_movie_name)

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.text(names[0])
        st.image(posters[0])
    with col2:
        st.text(names[1])
        st.image(posters[1])
    with col3:
        st.text(names[2])
        st.image(posters[2])
    with col4:
        st.text(names[3])
        st.image(posters[3])
    with col5:
        st.text(names[4])
        st.image(posters[4])

# Display default recommendations when the page loads
if not st.session_state.get('recommendations_loaded'):
    st.session_state.recommendations_loaded = True
    default_names, default_posters = fetch_default_movies()

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.text(default_names[0])
        st.image(default_posters[0])
    with col2:
        st.text(default_names[1])
        st.image(default_posters[1])
    with col3:
        st.text(default_names[2])
        st.image(default_posters[2])
    with col4:
        st.text(default_names[3])
        st.image(default_posters[3])
    with col5:
        st.text(default_names[4])
        st.image(default_posters[4])
