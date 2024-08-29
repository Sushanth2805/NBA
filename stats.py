import streamlit as st
from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats
import pandas as pd
import requests
from PIL import Image
from io import BytesIO

# Function to fetch the player's image with a higher resolution
def fetch_player_image(player_id):
    # Attempt to retrieve the image from NBA's CDN in higher resolution
    image_url_high_res = f"https://cdn.nba.com/headshots/nba/latest/1040x760/{player_id}.png"
    response = requests.get(image_url_high_res)
    
    if response.status_code == 200:
        img = Image.open(BytesIO(response.content))
        return img
    else:
        # Use a placeholder image if the player's image is not found
        return Image.open(BytesIO(requests.get("https://via.placeholder.com/200.png?text=No+Image").content))

# Streamlit application title
st.title("NBA Player Statistics")

# Input field for player name
player_name = st.text_input("Enter Player's Name")

if player_name:
    # Step 1: Find the player by name
    player = players.find_players_by_full_name(player_name)

    if player:
        # Get player details
        player_id = player[0]['id']
        player_data = player[0]

        # Safely access player attributes
        player_position = player_data.get('position', 'N/A')
        player_team = player_data.get('team', 'N/A')

        # Step 2: Fetch the player's image with higher resolution
        player_image = fetch_player_image(player_id)

        # Step 3: Fetch career statistics
        career_stats = playercareerstats.PlayerCareerStats(player_id=player_id)
        stats_df = career_stats.get_data_frames()[0]

        # Identify columns to sum from 'OREB' onwards
        relevant_columns = stats_df.columns[stats_df.columns.get_loc('OREB'):]

        # Calculate total row
        total_row = stats_df[relevant_columns].sum()
        total_row.name = 'Total'

        # Use pd.concat to add the total row
        stats_df = pd.concat([stats_df, total_row.to_frame().T])

        # Display player information
        st.image(player_image, caption=player_data['full_name'], width=400)  # Increase width for better viewing
        # Display the statistics with totals
        st.subheader("Career Statistics")
        st.dataframe(stats_df)

    else:
        st.error("Player not found. Please check the name and try again.")
