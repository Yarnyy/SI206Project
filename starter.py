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

# Fetch Spotify Global Top 50
def fetch_spotify_top_tracks():
    playlist_id = "1Cgey68pUlQGsCPI2wJuxr"
    results = sp.playlist_tracks(playlist_id=playlist_id, limit=30)
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

# Fetch Last.fm Top Tracks
def fetch_lastfm_top_tracks(country):
    params = {
        "method": "geo.gettoptracks",
        "country": country,
        "api_key": LASTFM_API_KEY,
        "format": "json",
        "limit": 30
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
        "maxResults": 30,
        "key": YOUTUBE_API_KEY
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

# TODO Store Data in Database


# SQLite Database Setup
conn = sqlite3.connect('music_data.db')
cursor = conn.cursor()

# TODO Create SQL Tables

# Load JSON data
with open('combined_music_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Create Spotify Table
cursor.execute('''CREATE TABLE IF NOT EXISTS Spotify (
               id INTEGER PRIMARY KEY,
               name TEXT,
               artists TEXT,
               popularity INTEGER,
               track_url TEXT)
               ''')

# Create Lastfm Table
cursor.execute('''CREATE TABLE IF NOT EXISTS Lastfm (
               id INTEGER PRIMARY KEY,
               name TEXT,
               duration INTEGER,
               listeners INTEGER,
               mbid TEXT,
               url TEXT,
               streamable TEXT,
               artist_name TEXT,
               artist_mbid TEXT,
               artist_url TEXT,
               image_small TEXT,
               image_medium TEXT,
               image_large TEXT,
               image_extralarge TEXT,
               track_url TEXT,
               rank INTEGER)
               ''')

# Create Youtube table
cursor.execute('''CREATE TABLE IF NOT EXISTS YouTube (
               id INTEGER PRIMARY KEY,
               title TEXT,
               channel TEXT,
               view_count INTEGER,
               video_url TEXT) 
               ''')

# Track number of rows
rows = {'spotify': 0, 'lastfm': 0, 'youtube': 0}

# Insert Spotify data and limit to 25 entries
for track in data['spotify'][:25]:
    cursor.execute('''INSERT INTO Spotify (name, artists, popularity, track_url)
                   VALUES (?, ?, ?, ?)''',
                   (track['name'],
                    ','.join(track['artists']),
                     track['popularity'],
                    track['track_url']))
    rows['spotify'] += 1

# Insert Lastfm data and limit to 25 entries
for track in data['lastfm'][:25]:
    cursor.execute('''INSERT INTO Lastfm (name, duration, listeners, mbid, url, streamable, artist_name, artist_mbid,
                                        artist_url, image_small, image_medium, image_large, image_extralarge, rank)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (track['name'],
                   int(track['duration']),
                   track['listeners'],
                   track['mbid'],
                   track['url'],
                   track['streamable']['#text'],
                   track['artist']['name'],
                   track['artist']['mbid'],
                   track['artist']['url'],
                   track['image'][0]['#text'], # image_small
                   track['image'][1]['#text'], # image_medium
                   track['image'][2]['#text'], # image_large
                   track['image'][3]['#text'], # image_extralarge
                   int(track['@attr']['rank'])))
    rows['lastfm'] += 1

# Insert Youtube data and limit to 25 entries
for track in data['youtube'][:25]:
    pass

conn.commit()
print("DB Commit Successful")
conn.close()

    # Spotify Data


    # Last.fm Data


    # YouTube Data


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
#TODO: Uncomment when ready to fetch new data

# Generate Visualizations

    # Spotify Popularity

    # YouTube View Count


    # Last.fm Genre Distribution
  

# Main Execution


