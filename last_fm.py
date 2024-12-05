import requests
import json
import sqlite3

API_KEY = "160e50d8eefda94217d780b3ad60e5ce"  # Replace with your Last.fm API key
BASE_URL = "http://ws.audioscrobbler.com/2.0/"

def fetch_and_store_regional_popular_songs(region_code="US", filename="regional_songs.json"):
    """Fetch popular tracks by region and store in a JSON file."""
    params = {
        "method": "chart.getTopTracks",
        "api_key": API_KEY,
        "country": region_code,
        "format": "json"
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        
        # Extract relevant data from the response
        songs_data = []
        tracks = response.json()['tracks']['track']
        for track in tracks:
            track_info = {
                "track_name": track['name'],
                "artist_name": track['artist']['name'],
                "url": track['url'],
                "genres": track.get('toptags', {}).get('tag', [])
            }
            songs_data.append(track_info)

            # Insert each track into the database
            insert_regional_song(
                track['name'], 
                track['artist']['name'], 
                region_code, 
                track['url'], 
                track.get('toptags', {}).get('tag', [])
            )
        
        
        # Write to a JSON file
        with open(filename, 'w') as file:
            json.dump(songs_data, file, indent=4)
        # print(f"Regional popular songs data stored in {filename}")
    
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except ValueError as e:
        print(f"Failed to parse JSON: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


def fetch_top_tracks_and_save_to_json(country):
    """Fetch top tracks by country, save them to a JSON file, and insert into SQL database."""
    params = {
        "method": "geo.gettoptracks",
        "country": country,
        "api_key": API_KEY,
        "format": "json"
    }

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        
        # Parse the JSON response
        data = response.json()
        
        if "tracks" in data:
            top_tracks = data['tracks']['track']
            
            # Save the data to a JSON file
            with open(f'top_tracks_{country}.json', 'w', encoding='utf-8') as f:
                json.dump(top_tracks, f, ensure_ascii=False, indent=4)
            print(f"Data successfully saved to 'top_tracks_{country}.json'")
            
            # Insert each track into the database
            for track in top_tracks:
                track_name = track['name']
                artist_name = track['artist']['name']
                listeners = int(track.get('listeners', 0))  # Default to 0 if not provided
                url = track['url']

                #insert into SQL database
                
                insert_top_track(track_name, artist_name, country, listeners, url)
        else:
            print("Error: Response does not contain the expected data.")
    
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except ValueError as e:
        print(f"Failed to parse JSON: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")



def fetch_and_store_trending_artists(region_code="US", filename="trending_artists.json"):
    """Fetch trending artists by region and store in a JSON file."""
    params = {
        "method": "chart.getTopArtists",
        "api_key": API_KEY,
        "country": region_code,
        "format": "json"
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        
        # Extract relevant data from the response
        artists_data = []
        artists = response.json()['artists']['artist']
        for artist in artists:
            artist_info = {
                "artist_name": artist['name'],
                "url": artist['url']
            }
            artists_data.append(artist_info)

        # Insert data into SQLite
        for artist in artists_data:
            insert_trending_artist(artist['artist_name'], artist['url'])
    
    
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except ValueError as e:
        print(f"Failed to parse JSON: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


def create_top_tracks_table():
    """Create a table for top tracks in specific countries."""
    conn = sqlite3.connect("music_data.db")
    cursor = conn.cursor()
    
    # Create a table for top tracks
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS top_tracks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            track_name TEXT NOT NULL,
            artist_name TEXT NOT NULL,
            country TEXT NOT NULL,
            url TEXT NOT NULL,
            genres TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()
    print("Top tracks table initialized.")
    
def create_regional_songs_table():
    """Create a table for regional popular songs in the SQLite database."""
    conn = sqlite3.connect("music_data.db")
    cursor = conn.cursor()
    
    # Create a table for regional songs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS regional_songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            track_name TEXT NOT NULL,
            artist_name TEXT NOT NULL,
            region_code TEXT NOT NULL,
            url TEXT NOT NULL,
            genres TEXT
        )
    """)
    
    conn.commit()
    conn.close()
    print("Regional songs table initialized.")


def create_trending_artists_table():
    """Create a table for trending artists in the SQLite database."""
    conn = sqlite3.connect("music_data.db")
    cursor = conn.cursor()
    
    # Create a table for trending artists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trending_artists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            artist_name TEXT NOT NULL,
            url TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()
    print("Trending artists table initialized.")

def insert_regional_song(track_name, artist_name, region_code, url, genres):
    """Insert a regional song into the SQLite database."""
    conn = sqlite3.connect("music_data.db")
    cursor = conn.cursor()
    
    genres_str = ", ".join([genre['name'] for genre in genres]) if isinstance(genres, list) else genres or ""
    
    cursor.execute("""
        INSERT INTO regional_songs (track_name, artist_name, region_code, url, genres)
        VALUES (?, ?, ?, ?, ?)
    """, (track_name, artist_name, region_code, url, genres_str))
    
    conn.commit()
    conn.close()
    print(f"Inserted regional song: {track_name} ({region_code})")

def insert_top_track(track_name, artist_name, country, url, genres):
    """Insert a top track into the SQLite database."""
    conn = sqlite3.connect("music_data.db")
    cursor = conn.cursor()
    
    genres_str = ", ".join([genre['name'] for genre in genres]) if isinstance(genres, list) else genres or ""
    
    cursor.execute("""
        INSERT INTO top_tracks (track_name, artist_name, country, url, genres)
        VALUES (?, ?, ?, ?, ?)
    """, (track_name, artist_name, country, url, genres_str))
    
    conn.commit()
    conn.close()
    # print(f"Inserted top track: {track_name} ({country})")


def insert_trending_artist(artist_name, url):
    """Insert a trending artist into the SQLite database."""
    conn = sqlite3.connect("music_data.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO trending_artists (artist_name, url)
        VALUES (?, ?)
    """, (artist_name, url))
    
    conn.commit()
    conn.close()
    # print(f"Inserted artist: {artist_name}")

if __name__ == "__main__":
    # Initialize tables
    create_trending_artists_table() #finished
    create_regional_songs_table() #finished
    create_top_tracks_table()
    
    # Fetch data and store it
    fetch_and_store_regional_popular_songs(region_code="US", filename="regional_playlists.json")

    fetch_and_store_trending_artists("US", "trending_artists_US.json") 

    fetch_top_tracks_and_save_to_json("United States")

    fetch_top_tracks_and_save_to_json("Spain")