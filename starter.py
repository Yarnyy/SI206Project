import sqlite3
import requests
from bs4 import BeautifulSoup
import json
import csv
import matplotlib.pyplot as plt

# Database setup, can be changed because it doesn't 100% work yet
def setup_database():
    conn = sqlite3.connect("music_data.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS MusicData (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            artist TEXT,
            album TEXT,
            source TEXT,
            cultural_impact TEXT,
            view_count INTEGER,
            UNIQUE(title, artist)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ArtistDetails (
            artist_id INTEGER PRIMARY KEY AUTOINCREMENT,
            artist_name TEXT UNIQUE,
            genre TEXT,
            popularity INTEGER
        )
    """)

    conn.commit()
    return conn

# Fetch data from YouTube API, gets the youtube data
def fetch_youtube_data(api_key):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": "top music",
        "type": "video",
        "key": api_key,
        "maxResults": 100
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        video_ids = [item["id"]["videoId"] for item in data.get("items", []) if "videoId" in item["id"]]
        video_details = fetch_youtube_video_details(api_key, video_ids)
        return video_details
    return []

# Fetch YouTube video statistics details based on view_count, artist details, and titles
def fetch_youtube_video_details(api_key, video_ids):
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "snippet,statistics",
        "id": ",".join(video_ids),
        "key": api_key
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return [
            {
                "title": item["snippet"]["title"],
                "artist": item["snippet"]["channelTitle"],
                "album": None,
                "source": "YouTube",
                "cultural_impact": "Popular on social media platforms",
                "view_count": int(item["statistics"]["viewCount"])
            }
            for item in data.get("items", [])
        ]
    return []

# Fetch data from Last.fm API, specifically the current top tracks
def fetch_lastfm_data(api_key):
    url = "http://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "chart.gettoptracks",
        "api_key": api_key,
        "format": "json",
        "limit": 100
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return [
            {"title": track["name"], "artist": track["artist"]["name"], "album": None, "source": "Last.fm", "cultural_impact": "Influential in streaming trends", "view_count": 0}
            for track in data.get("tracks", {}).get("track", [])
        ]
    return []

# Scrape data from Rolling Stone website for data on songs from artists that were involved in cultural movements.
# If this particular code doesn't work, go ahead and try looking into Genius API, i found it earlier and it seems to give lyrics that include cultural stuff


# Insert data into the database , again it is able to be changed because it isn't done
def insert_data(conn, data):
    cursor = conn.cursor()

    for item in data:

        # Insert into MusicData
        cursor.execute(
            "INSERT OR IGNORE INTO MusicData (title, artist, album, source, cultural_impact, view_count) VALUES (?, ?, ?, ?, ?, ?)",
            (item["title"], item["artist"], item["album"], item["source"], item["cultural_impact"], item["view_count"])
        )
        cursor.execute("SELECT id FROM MusicData WHERE title = ? AND artist = ?", (item["title"], item["artist"]))

# Query and calculate data
def query_and_calculate(conn):
    cursor = conn.cursor()
    query = """
        SELECT source, COUNT(*) as count
        FROM MusicData
        GROUP BY source
    """
    cursor.execute(query)
    result = cursor.fetchall()

    # Calculate average view count
    cursor.execute("SELECT AVG(view_count) FROM MusicData WHERE view_count > 0")
    avg_view_count = cursor.fetchone()[0]

    # Save results to a JSON file
    with open("data_summary.json", "w") as json_file:
        json.dump({"source_counts": {row[0]: row[1] for row in result}, "average_view_count": avg_view_count}, json_file, indent=4)

    return result, avg_view_count

# Create visualizations


# Main function
def main():
    conn = setup_database()

    youtube_api_key = 'AIzaSyAjHvWlEotJy5MVqi4WBX6iPRzQYivcY44'
    lastfm_api_key = "160e50d8eefda94217d780b3ad60e5ce" 

    youtube_data = fetch_youtube_data(youtube_api_key)
    lastfm_data = fetch_lastfm_data(lastfm_api_key)


    combined_data = youtube_data + lastfm_data 

    # Insert data into the database
    insert_data(conn, combined_data)

    # Query and calculate data
    result, avg_view_count = query_and_calculate(conn)
    print(f"Average view count across all sources: {avg_view_count}")

    # Create visualizations


    conn.close()

if __name__ == "__main__":
    main()


