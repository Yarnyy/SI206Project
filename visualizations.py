import json
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

with open('calculated_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Artist Popularity (Limit Top 30)
artist_popularity_list = pd.DataFrame(data['artist_popularity_list'][:30], columns=['artist', 'popularity_rating'])

# Sort popularity rating by descending
artist_popularity_list = artist_popularity_list.sort_values(by='popularity_rating', ascending=False)

# Bar chart
fig1 = px.bar(
    artist_popularity_list, 
    x='artist', 
    y='popularity_rating',
    labels={'artist': 'Artist','popularity_rating': 'Popularity Rating'},
    title='Spotify Artist Popularity')
fig1.show()

# Genre Rating
genre_ranks = pd.DataFrame(data['genre_ranks'], columns=['genre', 'rank'])

# Line graph
fig2 = px.line(
    genre_ranks,
    x='genre',
    y='rank',
    labels={'genre': 'Genre','rank': 'Rank'},
    title='Lastfm Genre Ranks (Lower = More Popular)',
    markers=True,
)

# Change color, line width and shape
fig2.update_traces(line_color='blue', line_width=2.5, line_shape='spline')
fig2.show()

# Top 5 Lastfm Artists
top5_lastfm_artists = pd.DataFrame(data['top5_lastfm_artists'], columns=['artist', 'listeners'])

# Pie chart
fig3 = px.pie(
    top5_lastfm_artists,
    values='listeners',
    names='artist',
    labels={'artist': 'Artist','listeners': 'Number of Listeners'},
)

# Add additional lables and increase font size 
fig3.update_traces(textinfo='label+percent', textfont_size=20, title={'text': 'Top 5 Lastfm Artists', 'font': {'size': 30}})
fig3.show()