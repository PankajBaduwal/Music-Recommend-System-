import pickle
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests

# Spotify API credentials
CLIENT_ID = "70a9fb89662f4dac8d07321b259eaad7"
CLIENT_SECRET = "4d6710460d764fbbb8d8753dc094d131"

# Initialize the Spotify client
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Function to get album cover URL and track link
def get_song_details(song_name, artist_name):
    search_query = f"track:{song_name} artist:{artist_name}"
    results = sp.search(q=search_query, type="track")

    if results and results["tracks"]["items"]:
        track = results["tracks"]["items"][0]
        album_cover_url = track["album"]["images"][0]["url"]
        track_url = track["external_urls"]["spotify"]
        embed_url = track["uri"]
        return album_cover_url, track_url, embed_url
    else:
        return "https://i.postimg.cc/0QNxYz4V/social.png", "#", ""

# Function to get song recommendations
def recommend(song):
    index = music[music['song'] == song].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_music_names = []
    recommended_music_posters = []
    recommended_music_links = []
    recommended_music_embeds = []
    
    for i in distances[1:6]:
        artist = music.iloc[i[0]].artist
        song_name = music.iloc[i[0]].song
        poster, link, embed = get_song_details(song_name, artist)
        recommended_music_posters.append(poster)
        recommended_music_names.append(song_name)
        recommended_music_links.append(link)
        recommended_music_embeds.append(embed)

    return recommended_music_names, recommended_music_posters, recommended_music_links, recommended_music_embeds

# Function to generate song description using OpenAI's GPT model
def generate_description(song_name):
    openai_api_key = "your_openai_api_key"  # Replace with your OpenAI API key
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {openai_api_key}"},
        json={
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": f"Describe the song '{song_name}' in an engaging way."}],
            "max_tokens": 100,
            "temperature": 0.7,
        }
    )
    
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return "No description available."

# App layout and styling
st.markdown(
    """
    <style>
    .main {
        background-color: #191414;
        color: #1DB954;
        font-family: 'Arial', sans-serif;
    }
    h1, h2 {
        color: #1DB954;
    }
    .footer {
        color: #999999;
        font-size: 0.9em;
        text-align: center;
        margin-top: 20px;
    }
    .song-link {
        text-decoration: none;
        color: #1DB954;
        font-weight: bold;
    }
    .song-link:hover {
        color: #FFFFFF;
    }
    iframe {
        border-radius: 10px;
    }
    .song-container {
        display: flex;
        justify-content: space-between;
        margin-bottom: 20px;
    }
    .song-item {
        flex: 1;
        margin: 0 10px;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# App title and description
st.title('🎵 Music Recommender System')
st.subheader('Discover and play songs similar to your favorites')

# Load data
music = pickle.load(open('df.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Song selection
music_list = music['song'].values
selected_song = st.selectbox("Select or type a song you like:", music_list)

# Recommendation button
if st.button('Show Recommendations'):
    with st.spinner('Finding your recommendations...'):
        recommended_music_names, recommended_music_posters, recommended_music_links, recommended_music_embeds = recommend(selected_song)

        # Generate descriptions for each recommended song
        descriptions = [generate_description(name) for name in recommended_music_names]

        # Display recommendations in rows of three
        for i in range(0, len(recommended_music_names), 3):
            with st.container():
                row_items = recommended_music_names[i:i+3]
                posters = recommended_music_posters[i:i+3]
                links = recommended_music_links[i:i+3]
                embeds = recommended_music_embeds[i:i+3]
                descs = descriptions[i:i+3]

                st.markdown('<div class="song-container">', unsafe_allow_html=True)

                for j in range(len(row_items)):
                    st.markdown(
                        f"""
                        <div class="song-item">
                            <h3>{row_items[j]}</h3>
                            <p>{descs[j]}</p>
                            <img src="{posters[j]}" width="200"/>
                            <br/>
                            <a href="{links[j]}" target="_blank" class="song-link">Play on Spotify</a>
                            <br/>
                            <iframe src="https://open.spotify.com/embed/track/{embeds[j].split(':')[-1]}" width="300" height="80" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown('<p class="footer">Made by Mr.Pankaj Baduwal</p>', unsafe_allow_html=True)