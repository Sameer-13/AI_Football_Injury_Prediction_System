import streamlit as st
import pandas as pd

def display_player_table(player_df):
    """
    Display a table of players with injury predictions
    
    Args:
        team_players: DataFrame containing player data for a specific team
        
    Returns:
        DataFrame: Processed player display DataFrame
    """
    st.markdown("### Player Injury Risk Assessment")


   # Color function for styling
    def color_injury_prediction(val):
        if val == 'High Risk':
            return 'background-color: #E74C3C; color: white; font-weight: bold'  # Soft red
        else:
            return 'background-color: #5DB85C; color: white; font-weight: bold'  # Fresh green
        
    # Style and display the DataFrame
    styled_df_display = (
        player_df.drop(columns=['Injury Prediction'])
        .style
        .applymap(color_injury_prediction, subset=["Injury Risk"])
        .set_properties(**{'text-align': 'center'})  # Center text in all cells
    )

    # Center column headers (optional, Streamlit may auto-style headers differently)
    styled_df_display.set_table_styles(
        [{'selector': 'th', 'props': [('text-align', 'center')]}]
    )

    st.dataframe(styled_df_display, use_container_width=True)
    
    return player_df