import requests
import json
import sqlite3

API_KEY = "160e50d8eefda94217d780b3ad60e5ce"  # Replace with your Last.fm API key
BASE_URL = "http://ws.audioscrobbler.com/2.0/"

# Functions to fetch data and store it into JSON files
def fetch_and_store_top_tracks(artist_name, filename="top_tracks.json"):
    """Fetch top tracks of an artist and store in a JSON file."""
    params = {
        "method": "artist.getTopTracks",
        "api_key": API_KEY,
        "artist": artist_name,
        "format": "json"
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        
        # Extract relevant data from the response
        tracks_data = []
        tracks = response.json()['toptracks']['track']
        for track in tracks:
            track_info = {
                "track_name": track['name'],
                "artist_name": track['artist']['name'],
                "url": track['url'],
                "genres": track.get('toptags', {}).get('tag', [])
            }
            tracks_data.append(track_info)
        
        # Write to a JSON file
        with open(filename, 'w') as file:
            json.dump(tracks_data, file, indent=4)
        print(f"Top tracks data stored in {filename}")
    
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except ValueError as e:
        print(f"Failed to parse JSON: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


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
        
        # Write to a JSON file
        with open(filename, 'w') as file:
            json.dump(songs_data, file, indent=4)
        print(f"Regional popular songs data stored in {filename}")
    
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except ValueError as e:
        print(f"Failed to parse JSON: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


def fetch_top_tracks_and_save_to_json(country):
    """Fetch top tracks by country and save them to a JSON file."""
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
        
        # Write to a JSON file
        with open(filename, 'w') as file:
            json.dump(artists_data, file, indent=4)
        print(f"Trending artists data stored in {filename}")
    
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except ValueError as e:
        print(f"Failed to parse JSON: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


# Functions to fetch data and store it into JSON files
def fetch_and_store_top_tracks(artist_name, filename="top_tracks.json"):
    """Fetch top tracks of an artist and store in a JSON file."""
    params = {
        "method": "artist.getTopTracks",
        "api_key": API_KEY,
        "artist": artist_name,
        "format": "json"
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        
        # Extract relevant data from the response
        tracks_data = []
        tracks = response.json()['toptracks']['track']
        for track in tracks:
            track_info = {
                "track_name": track['name'],
                "artist_name": track['artist']['name'],
                "url": track['url'],
                "genres": track.get('toptags', {}).get('tag', [])
            }
            tracks_data.append(track_info)
        
        # Write to a JSON file
        with open(filename, 'w') as file:
            json.dump(tracks_data, file, indent=4)
        print(f"Top tracks data stored in {filename}")
        
        # Insert data into SQLite
        for track in tracks_data:
            insert_track(track['track_name'], track['artist_name'], track['url'], track['genres'])
    
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except ValueError as e:
        print(f"Failed to parse JSON: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


## TODO : Create SQL code 

# Main function to fetch and store data into JSON files and load into SQLite
def main():
    fetch_top_tracks_and_save_to_json("spain")
    fetch_top_tracks_and_save_to_json('United States')
    fetch_and_store_trending_artists(region_code="", filename="trending_artists.json")
    fetch_and_store_top_tracks('The Weeknd', filename="top_tracks")

