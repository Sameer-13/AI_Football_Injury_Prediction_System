import streamlit as st
import pandas as pd

def display_player_table(team_players):
    """
    Display a table of players with injury predictions
    
    Args:
        team_players: DataFrame containing player data for a specific team
        
    Returns:
        DataFrame: Processed player display DataFrame
    """
    st.markdown("### Player Injury Risk Assessment")
    
    # Select columns for display
    player_display_df = team_players[['player_id', 'position', 'prev_player_age', 
                                      'prev_player_height', 'prev_player_weight',
                                      'prev_games_appearences', 'prev_games_minutes',
                                      'prev_games_rating', 'injuried']].copy()

    # Rename columns for display
    player_display_df = player_display_df.rename(columns={
        'player_id': 'Player ID',
        'position': 'Position',
        'prev_player_age': 'Age',
        'prev_player_height': 'Height (cm)',
        'prev_player_weight': 'Weight (kg)',
        'prev_games_appearences': 'Appearances',
        'prev_games_minutes': 'Minutes Played',
        'prev_games_rating': 'Rating',
        'injuried': 'Injury Prediction'
    })

    # Add readable risk label
    player_display_df['Injury Risk'] = player_display_df['Injury Prediction'].apply(
        lambda x: 'High Risk' if x == 1 else 'Low Risk'
    )

    # Color function for styling
    def color_injury_prediction(val):
        color = 'red' if val == 'High Risk' else 'green'
        return f'background-color: {color}; color: white; font-weight: bold'

    # Style and display the DataFrame
    styled_df_display = player_display_df.drop(columns=['Injury Prediction']).style.applymap(
        color_injury_prediction, subset=["Injury Risk"]
    )

    st.dataframe(styled_df_display, use_container_width=True)
    
    return player_display_df