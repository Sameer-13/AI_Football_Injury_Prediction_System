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
                
                # Create a card in this column
                with cols[j]:
                    # Custom styled card using HTML
                    st.markdown(
                        f"""
                        <div style="
                            background-color: #1E2130;
                            padding: 20px;
                            border-radius: 10px;
                            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                            text-align: center;
                        ">
                            <h3 style="margin-bottom: 5px;">Player {player_id}</h3>
                            <p style="color: gray; margin: 0;">{position}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    # Add space between cards
                    st.write("")
        
        # Add space between rows
        st.write("")

def format_value(value, decimal_places=0):
    """Format a value to the specified number of decimal places"""
    if isinstance(value, (int, float)):
        return f"{value:.{decimal_places}f}"
    return value
