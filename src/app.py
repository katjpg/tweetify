import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from collections import Counter
import ast 

# set dark template for plotly
import plotly.io as pio
pio.templates.default = 'plotly_dark'

# load data 
AUDIO_DF = pd.read_csv('data/processed/audio-feat/US_2022_audio.csv')
GENRE_DF = pd.read_csv('data/processed/genres/US_2022_genres.csv')
POP_DF = pd.read_csv('data/processed/track-info/US_2022_track_info.csv')
STREAM_DF = pd.read_csv('data/processed/location/US_2022_geoloc.csv')

# cluster playlists
CLUSTERS = {
    "cluster 1": "https://open.spotify.com/embed/playlist/77Y4B9MW29cZNDnArr2piu?utm_source=generator",
    "cluster 2": "https://open.spotify.com/embed/playlist/5rbgPmbxv7KbUJu9NDHiTG?utm_source=generator",
    "cluster 3": "https://open.spotify.com/embed/playlist/7oI3DvWCNMBuM2YapihaYm?utm_source=generator",
    "cluster 4": "https://open.spotify.com/embed/playlist/48Rl526DDwEAidEeqPZhci?utm_source=generator",
    "cluster 5": "https://open.spotify.com/embed/playlist/4snq3ClP8sPFlY81LjARkf?utm_source=generator",
}

def genre_count(df):
    """Generate a bar chart of the top 25 genres."""
    genre_counter = Counter()
    
    for genres_string in df['genres']:
        genres_list = ast.literal_eval(genres_string)
        if genres_list:
            genre_counter.update(genres_list)
    
    genres, counts = zip(*genre_counter.most_common(25))

    fig = go.Figure(data=go.Bar(
        y=genres,
        x=counts,
        orientation='h',
        marker=dict(
            color=counts,
            colorscale='tealgrn',
            line_width=0
        )
    ))

    fig.update_layout(
        title={"text": "Top 25 Genres", 'x': 0.5, 'xanchor': 'center'},
        xaxis_title="Count",
        yaxis_title="Genre",
        yaxis={'categoryorder':'total ascending', 'nticks': len(genres)},
    )

    return fig

def radar_chart(df):
    """Generate a radar chart of mean audio features."""
    cols = ['danceability', 'energy', 'liveness', 'valence', 'acousticness', 'speechiness', 'instrumentalness']
    df_mean = ((df[cols] - df[cols].min()) / (df[cols].max() - df[cols].min())).mean() * 100
    
    fig = go.Figure(data=go.Scatterpolar(
        r=df_mean.values,
        theta=cols,
        hovertemplate='%{customdata}<extra></extra>',
        customdata=['{}: {}'.format(col, val) for col, val in zip(cols, df_mean.values)],
        fill='toself',
        line_color='#05d7f3'
    ))

    fig.update_layout(
        title={"text": "Mean Audio Features", 'x': 0.5, 'xanchor': 'center'},
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False
    )

    return fig

def pop_hist(df):
    """Generate a histogram of popularity distribution, excluding 0 popularity."""
    df = df[df['popularity'] != 0]
    counter = Counter(df['popularity'])
    popularity_scores, counts = zip(*sorted(counter.items()))
    max_count = max(counts)

    fig = go.Figure(data=go.Bar(
        x=popularity_scores,
        y=counts,
        marker_color=[f'rgba(5, 215, 243, {i**0.5/max_count**0.5})' for i in counts]
    ))

    fig.update_layout(
        title={"text": "Popularity Distribution", 'x': 0.5, 'xanchor': 'center'},
        xaxis_title="Popularity",
        yaxis_title="Count",
        bargap=0.05,
        width=1200,
        height=500
    )

    return fig

def bubble_map(df):
    """Generate a bubble map showing the geographical distribution of Spotify stream tweets."""
    df['state_id'] = df['state_id'].str.upper()
    df_counts = df.groupby(['city', 'state_id', 'lat', 'lng']).size().reset_index(name='counts')

    fig = go.Figure(data=go.Scattergeo(
        lat=df_counts['lat'],
        lon=df_counts['lng'],
        text=df_counts['city'] + ', ' + df_counts['state_id'],
        mode='markers',
        marker=dict(
            size=df_counts['counts'],
            color=df_counts['counts'],
            colorscale='tealgrn',
            sizemode='area',
            sizeref=2. * max(df_counts['counts']) / (40. ** 2),
            sizemin=4,
            showscale=True,
            colorbar=dict(title="Counts"),
            cmin=df_counts['counts'].min(),
            cmax=df_counts['counts'].max()
        )
    ))

    fig.update_geos(scope='usa')
    fig.update_layout(
        title={"text": "Geographical Distribution of Spotify Stream Tweets", 'x': 0.5, 'xanchor': 'center'},
        geo=dict(
            landcolor='rgb(217, 217, 217)',
            subunitcolor='rgb(217, 217, 217)',
            countrycolor='rgb(217, 217, 217)',
            showlakes=True,
            lakecolor='rgb(255, 255, 255)',
            showsubunits=True
        ),
        width=1200,
        height=700
    )

    return fig

# =============== APP ===============

def overview_page():
    st.title('Twitter 2022 Wrapped')
    st.markdown('### 🎉 Introducing Twitter Wrapped 2022! 🎉')

    st.plotly_chart(bubble_map(STREAM_DF))

    col1, col2 = st.columns(spec=[0.9, 0.1], gap='large')
    with col1:
        st.plotly_chart(genre_count(GENRE_DF))
    with col2:
        st.plotly_chart(radar_chart(AUDIO_DF))

    st.plotly_chart(pop_hist(POP_DF))

def playlist_page():
    st.title('Tweetify Curated Playlists')
    st.markdown("### Select a cluster to view its Spotify playlist:")

    selected_cluster = st.selectbox("Choose a cluster", list(CLUSTERS.keys()))
    st.markdown(f"""
    <iframe 
        style="border-radius:12px" 
        src="{CLUSTERS[selected_cluster]}" 
        width="100%" 
        height="352" 
        frameBorder="0" 
        allowfullscreen="" 
        allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" 
        loading="lazy">
    </iframe>
    """, unsafe_allow_html=True)

def app():
    st.sidebar.image("img/tweetify.png", use_column_width=True) 
    st.sidebar.title('Tweetify: Mapping the Intersection of Twitter and Spotify')

    st.markdown("""
    <style>
    [data-testid="stSidebar"][role="navigation"] {
        width: 20rem;
        max-width: 20rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    PAGES = {
        "Overview": overview_page,
        "Playlist": playlist_page,
    }
    
    selection = st.sidebar.radio("Go to", list(PAGES.keys()))
    page_func = PAGES[selection]
    page_func()

if __name__ == "__main__":
    app()