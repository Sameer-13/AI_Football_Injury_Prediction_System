import streamlit as st
import pandas as pd

def display_player_cards(high_risk_players):
    """
    Display player cards using Streamlit's built-in components
    
    Args:
        high_risk_players: DataFrame containing high-risk player data
    """
    # Add some space before the cards
    st.write("")
    
    # Create a grid of cards using columns
    for i in range(0, len(high_risk_players), 3):
        # Create a row with 3 columns
        cols = st.columns(3)
        
        # Process up to 3 players per row
        for j in range(3):
            idx = i + j
            if idx < len(high_risk_players):
                player = high_risk_players.iloc[idx]
                
                # Get values with proper formatting
                player_id = player.get('Player ID', 'Unknown')
                position = player.get('Position', 'Not Specified')
                age = format_value(player.get('Age', 'N/A'), 0)
                rating = format_value(player.get('Rating', 'N/A'), 2)
                height = format_value(player.get('Height (cm)', 'N/A'), 0)
                weight = format_value(player.get('Weight (kg)', 'N/A'), 0)
                
                # Create a card in this column
                with cols[j]:
                    # Use a container for styling
                    with st.container():
                        # Player header
                        st.subheader(f"Player {player_id}")
                        st.caption(position)
                    
                    # Add space between cards
                    st.write("")
        
        # Add space between rows
        st.write("")

def format_value(value, decimal_places=0):
    """Format a value to the specified number of decimal places"""
    if isinstance(value, (int, float)):
        return f"{value:.{decimal_places}f}"
    return value