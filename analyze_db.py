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

# Calc avg popularity by artist
cursor.execute('''
               SELECT SpotifyArtists.name AS artist_name, AVG(SpotifyTracks.popularity) AS avg_popularity
               FROM SpotifyTracks
               JOIN SpotifyArtists ON SpotifyTracks.track_id = SpotifyArtists.track_id
               GROUP BY SpotifyArtists.name
               ''')
artist_popularity_list = cursor.fetchall()

# Fetch most popular songs and their Lastfm ranks
cursor.execute('''
               SELECT genres, rank
               FROM Lastfm
               ''')
genre_ranks = cursor.fetchall()

# Fetch top 5 artists by Lastfm listeners
cursor.execute('''
               SELECT artist_name, listeners
               FROM Lastfm
               ORDER BY listeners DESC
               LIMIT 5
               ''')
top5_lastfm_artists = cursor.fetchall()

data = {
    "avg_spotify_popularity": avg_spotify_popularity,
    "total_lastfm_listeners": total_lastfm_listeners,
    "most_viewed_yt_channel": {
        "channel": most_viewed_channel[0],
        "view_count": most_viewed_channel[1]
    },
    "artist_popularity_list": artist_popularity_list,
    "genre_ranks": genre_ranks,
    "top5_lastfm_artists": top5_lastfm_artists
}

# Write calculations to JSON file 
with open('calculated_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("calculated_data.json written to successfully")

# Close connection to database
conn.close()