import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
import requests
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
# cursor.execute('DELETE FROM Artists')
# cursor.execute('DELETE FROM Genres')

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
               FOREIGN KEY (artist_id) REFERENCES Artists(artist_id),
               FOREIGN KEY (track_id) REFERENCES SpotifyTracks(track_id),
               UNIQUE (track_id, artist_id)
               )
               ''')

# Create Genres Table
cursor.execute('''CREATE TABLE IF NOT EXISTS Genres (
               genre_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
               name TEXT UNIQUE
               )
               ''')

# Create Lastfm Table
cursor.execute('''CREATE TABLE IF NOT EXISTS Lastfm (
               id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
               name TEXT UNIQUE,
               listeners INTEGER,
               artist_id INTEGER,
               rank INTEGER,
               genre_id INTEGER,
               FOREIGN KEY (artist_id) REFERENCES Artists(artist_id),
               FOREIGN KEY (genre_id) REFERENCES Genres(genre_id)
               )
               ''')

# Create Artists Table
cursor.execute('''CREATE TABLE IF NOT EXISTS Artists (
               artist_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
               name TEXT UNIQUE
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
def get_current_rows(table):
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    return cursor.fetchone()[0]

spotify_tracks_count = get_current_rows('SpotifyTracks')
spotify_artists_count = get_current_rows('SpotifyArtists')
lastfm_count = get_current_rows('Lastfm')
artist_count = get_current_rows('Artists')
genre_count = get_current_rows('Genres')
youtube_count = get_current_rows('YouTube')

# Initialize row counters
total_rows_added = 0
max_rows = 25

# Insert Spotify data and limit to 10 entries
for track in data['spotify'][spotify_tracks_count: spotify_tracks_count + 10]:
    
    # Stop if 25 rows in database
    if total_rows_added >= max_rows: break
    
    cursor.execute('''INSERT OR IGNORE INTO SpotifyTracks (name, popularity)
                   VALUES (?, ?)''',
                   (track['name'], track['popularity']))
    
    # Increment when a row is added
    if cursor.rowcount > 0: total_rows_added += 1

    # Check again if limit is reached
    if total_rows_added >= max_rows: break

    track_id = cursor.lastrowid # Get id of current AUTOINCREMENT insert

    for artist in track['artists'][spotify_artists_count:]:
        if total_rows_added >= max_rows: break

        cursor.execute('''INSERT OR IGNORE INTO Artists (name) VALUES (?)''', (artist,))
        if cursor.rowcount > 0: total_rows_added += 1
        if total_rows_added >= max_rows: break

        cursor.execute('''SELECT artist_id FROM Artists WHERE name = ?''', (artist,))
        artist_id = cursor.fetchone()[0]

        cursor.execute('''INSERT OR IGNORE INTO SpotifyArtists (track_id, artist_id)
                       VALUES (?, ?)''',
                       (track_id, artist_id)) 
        if cursor.rowcount > 0: total_rows_added += 1
        if total_rows_added >= max_rows: break

# Insert Lastfm data and limit to 4 entries
for track in data['lastfm'][lastfm_count: lastfm_count + 4]:
    if total_rows_added >= max_rows: break

    # Create artist_id and prevent duplicates
    cursor.execute('''INSERT OR IGNORE INTO Artists (name) VALUES (?)''', (track['artist']['name'],))
    if cursor.rowcount > 0: total_rows_added += 1
    if total_rows_added >= max_rows: break

    cursor.execute('''SELECT artist_id FROM Artists WHERE name = ?''', (track['artist']['name'],))
    artist_id = cursor.fetchone()[0]

    # Create genre_id and prevent duplicates
    cursor.execute('''INSERT OR IGNORE INTO Genres (name) VALUES (?)''', (track['genres'][0],)) # First assigned genre
    if cursor.rowcount > 0: total_rows_added += 1
    if total_rows_added >= max_rows: break

    cursor.execute('''SELECT genre_id FROM Genres WHERE name = ?''', (track['genres'][0],))
    genre_id = cursor.fetchone()[0]

    # Fill Lastfm with data and ids 
    cursor.execute('''INSERT OR IGNORE INTO Lastfm (name, listeners, artist_id, rank, genre_id)
                   VALUES (?, ?, ?, ?, ?)''',
                   (track['name'],
                   track['listeners'],
                   artist_id,
                   int(track['@attr']['rank']),
                   genre_id)) 
    if cursor.rowcount > 0: total_rows_added += 1

# Insert Youtube data
for track in data['youtube'][youtube_count:]:
    if total_rows_added >= max_rows: break
    
    cursor.execute('''INSERT OR IGNORE INTO YouTube (title, channel, view_count)
                   VALUES (?, ?, ?)''',
                   (track['title'],
                    track['channel'],
                    track['view_count']))
    if cursor.rowcount > 0: total_rows_added += 1
    if total_rows_added >= max_rows: break

# Commit changes and close database
conn.commit()

total_db_rows = (get_current_rows('SpotifyTracks') + 
                 get_current_rows('SpotifyArtists') +
                 get_current_rows('Lastfm') + 
                 get_current_rows('Artists') + 
                 get_current_rows('Genres') +
                 get_current_rows('YouTube'))

print(f"Rows Added: {total_rows_added}")
print(f"Total number of rows in the database: {total_db_rows}")

# Close database connection
conn.close()