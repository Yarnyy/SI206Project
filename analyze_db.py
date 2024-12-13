import sqlite3
import json

# SQLite Database Setup
conn = sqlite3.connect('music_data.db')
cursor = conn.cursor()

# Calc avg popularity of Spotify tracks
cursor.execute('SELECT AVG(popularity) FROM SpotifyTracks')
avg_spotify_popularity = cursor.fetchone()[0]

# Calc total number of Lastfm listeners
cursor.execute('SELECT SUM(listeners) FROM Lastfm')
total_lastfm_listeners = cursor.fetchone()[0]

# Fetch YouTube channel with highest view count
cursor.execute('SELECT channel, MAX(view_count) FROM YouTube')
most_viewed_channel = cursor.fetchone()

# Join SpotifyTracks & SpotifyArtists
cursor.execute('''SELECT SpotifyTracks.name, SpotifyArtists.name AS artist_name
               FROM SpotifyTracks
               JOIN SpotifyArtists ON SpotifyTracks.track_id = SpotifyArtists.track_id
               ''')
tracks_artists_list = cursor.fetchall()

data = {
    "avg_spotify_popularity": avg_spotify_popularity,
    "total_lastfm_listeners": total_lastfm_listeners,
    "most_viewed_yt_channel": {
        "channel": most_viewed_channel[0],
        "view_count": most_viewed_channel[1]
    },
    "Spotify Tracks & Artists": tracks_artists_list
}

# Write calculations to JSON file 
with open('calculated_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("calculated_data.json written to successfully")

# Close connection to database
conn.close()