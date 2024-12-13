import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
import requests
import matplotlib.pyplot as plt
import pandas as pd
from pandas import json_normalize
import sqlite3

# Spotify API Credentials
SPOTIPY_CLIENT_ID = 'b58820404e894a63b5cf48ec5afe52e9'
SPOTIPY_CLIENT_SECRET = 'c6e18a4230704f9b898803bf2977f200'

# YouTube API Credentials
YOUTUBE_API_KEY = 'AIzaSyAjHvWlEotJy5MVqi4WBX6iPRzQYivcY44'
YOUTUBE_BASE_URL = "https://www.googleapis.com/youtube/v3"

# Last.fm API Credentials
LASTFM_API_KEY = "160e50d8eefda94217d780b3ad60e5ce" 
LASTFM_BASE_URL = "https://ws.audioscrobbler.com/2.0/"

# Spotify Setup
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET
))

# Fetch Spotify Global Top 100
def fetch_spotify_top_tracks():
    playlist_id = "1Cgey68pUlQGsCPI2wJuxr"
    results = sp.playlist_tracks(playlist_id=playlist_id, limit=100)
    top_tracks = [
        {
            "name": track['track']['name'],
            "artists": [artist['name'] for artist in track['track']['artists']],
            "popularity": track['track']['popularity'],
            "track_url": track['track']['external_urls']['spotify']
        }
        for track in results['items']
    ]
    return top_tracks

# Fetch Last.fm Top 50 Tracks
def fetch_lastfm_top_tracks(country):
    params = {
        "method": "geo.gettoptracks",
        "country": country,
        "api_key": LASTFM_API_KEY,
        "format": "json",
        "limit": 50
    }
    response = requests.get(LASTFM_BASE_URL, params=params)
    data = response.json()
    if "tracks" in data:
        return data["tracks"]["track"]
    
    return []

# Fetch Genres for Last.fm Tracks
def fetch_lastfm_genres(top_tracks):
    tracks_with_genres = []
    for track in top_tracks:
        track_name = track['name']
        artist_name = track['artist']['name']
        params = {
            "method": "track.getInfo",
            "track": track_name,
            "artist": artist_name,
            "api_key": LASTFM_API_KEY,
            "format": "json"
        }
        response = requests.get(LASTFM_BASE_URL, params=params)
        track_data = response.json()
        genres = [tag["name"] for tag in track_data.get("track", {}).get("toptags", {}).get("tag", [])]
        track["genres"] = genres
        tracks_with_genres.append(track)

    return tracks_with_genres

# Fetch YouTube Popular Music Videos
def fetch_youtube_videos(region_code="US"):
    params = {
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "regionCode": region_code,
        "videoCategoryId": "10",  # Music category
        "maxResults": 50,
        "key": YOUTUBE_API_KEY,
    }
    response = requests.get(f"{YOUTUBE_BASE_URL}/videos", params=params)
    data = response.json()
    if "items" in data:
        return [
            {
                "title": video["snippet"]["title"],
                "channel": video["snippet"]["channelTitle"],
                "view_count": int(video["statistics"]["viewCount"]),
                "video_url": f"https://www.youtube.com/watch?v={video['id']}"
            }
            for video in data["items"]
        ]
    return []

# Combine Data and Save as JSON
def combine_and_save_data():
    spotify_data = fetch_spotify_top_tracks()
    lastfm_tracks = fetch_lastfm_top_tracks("United States")
    lastfm_data = fetch_lastfm_genres(lastfm_tracks)
    youtube_data = fetch_youtube_videos()

    combined_data = {
        "spotify": spotify_data,
        "lastfm": lastfm_data,
        "youtube": youtube_data
    }

    with open("combined_music_data.json", "w", encoding="utf-8") as f:
        json.dump(combined_data, f, ensure_ascii=False, indent=4)

    print("Data successfully saved to 'combined_music_data.json'")
    return combined_data

# combine_and_save_data()
# NOTE: Uncomment when ready to refresh JSON contents


# SQLite Database Setup
conn = sqlite3.connect('music_data.db')
cursor = conn.cursor()

# Load JSON data
with open('combined_music_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Delete existing data
# cursor.execute('DELETE FROM SpotifyArtists')
# cursor.execute('DELETE FROM SpotifyTracks')
# cursor.execute('DELETE FROM Lastfm')
# cursor.execute('DELETE FROM YouTube')

# Create SpotifyTracks Table
cursor.execute('''CREATE TABLE IF NOT EXISTS SpotifyTracks (
               track_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
               name TEXT UNIQUE,
               popularity INTEGER
               )
               ''')

# Create SpotifyArtists Table
cursor.execute('''CREATE TABLE IF NOT EXISTS SpotifyArtists (
               artist_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
               track_id INTEGER,
               name TEXT UNIQUE,
               FOREIGN KEY (track_id) REFERENCES SpotifyTracks(track_id)
               )
               ''')

# Create Lastfm Table
cursor.execute('''CREATE TABLE IF NOT EXISTS Lastfm (
               id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
               name TEXT UNIQUE,
               listeners INTEGER,
               artist_name TEXT UNIQUE,
               rank INTEGER,
               genres TEXT UNIQUE
               )
               ''')

# Create Youtube table
cursor.execute('''CREATE TABLE IF NOT EXISTS YouTube (
               id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
               title TEXT UNIQUE,
               channel TEXT UNIQUE,
               view_count INTEGER
               ) 
               ''')

# Track number of rows in each table
row_count = {'spotify_tracks': 0, 'lastfm': 0, 'youtube': 0}

def get_current_rows(table):
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    return cursor.fetchone()[0]

spotify_count = get_current_rows('SpotifyTracks')
lastfm_count = get_current_rows('Lastfm')
youtube_count = get_current_rows('YouTube')

# Insert Spotify data and limit to 25 entries
for track in data['spotify'][spotify_count:spotify_count + 25]:
    cursor.execute('''INSERT OR IGNORE INTO SpotifyTracks (name, popularity)
                   VALUES (?, ?)''',
                   (track['name'],
                    track['popularity']))
    track_id = cursor.lastrowid # Get id of current AUTOINCREMENT insert
    for artist in track['artists']:
        cursor.execute('''INSERT OR IGNORE INTO SpotifyArtists (track_id, name)
                       VALUES (?, ?)''',
                       (track_id,
                        artist))    
    row_count['spotify_tracks'] += 1                   

# Insert Lastfm data and limit to 25 entries
for track in data['lastfm'][lastfm_count:lastfm_count + 25]:
    cursor.execute('''INSERT OR IGNORE INTO Lastfm (name, listeners, artist_name, rank, genres)
                   VALUES (?, ?, ?, ?, ?)''',
                   (track['name'],
                   track['listeners'],
                   track['artist']['name'],
                   int(track['@attr']['rank']),
                   track['genres'][0])) # First assigned genre
    row_count['lastfm'] += 1

# Insert Youtube data and limit to 25 entries
for track in data['youtube'][youtube_count:youtube_count + 25]:
    cursor.execute('''INSERT OR IGNORE INTO YouTube (title, channel, view_count)
                   VALUES (?, ?, ?)''',
                   (track['title'],
                    track['channel'],
                    track['view_count']))
    row_count['youtube'] += 1

# Commit changes and close database
conn.commit()
print(f"Added {row_count['spotify_tracks']} Spotify rows")
print(f"Added {row_count['lastfm']} Lastfm rows")
print(f"Added {row_count['youtube']} YouTube rows")

# cursor.execute('SELECT AVG(popularity) FROM Spotify')

# cursor.execute('SELECT ')

# avg_spotify_popularity = cursor.fetchone()[0]

conn.close()

# Generate Visualizations

    # Spotify Popularity


    # YouTube View Count


    # Last.fm Genre Distribution
  

# Main Execution


