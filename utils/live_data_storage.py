import pandas as pd
import streamlit as st
import os

def get_stored_live_data(team_name):
    """
    Retrieve stored live match data for a team from session state.
    Creates a new empty dataframe if none exists.
    
    Args:
        team_name: Name of the team to get data for
        
    Returns:
        DataFrame: Historical live match data
    """
    # Create a session key for this team
    session_key = f"live_data_{team_name.replace(' ', '_')}"
    
    # Initialize if not exists
    if session_key not in st.session_state:
        st.session_state[session_key] = pd.DataFrame(
            columns=['minute', 'player_name', 'risk_score', 'rank']
        )
    
    return st.session_state[session_key]

def update_stored_live_data(team_name, new_data):
    """
    Update stored live match data with new data.
    Merges new data with existing data, keeping unique minute/player combinations.
    
    Args:
        team_name: Name of the team to update data for
        new_data: DataFrame containing new live match data
        
    Returns:
        DataFrame: Updated historical live match data
    """
    # Get current stored data
    stored_data = get_stored_live_data(team_name)
    
    # Check if new_data is valid
    if new_data is None or new_data.empty:
        return stored_data
    
    # Ensure we have required columns
    required_columns = ['minute', 'player_name', 'risk_score', 'rank']
    for col in required_columns:
        if col not in new_data.columns:
            return stored_data
    
    # If this is new data for a minute we haven't seen, append it
    latest_minute = new_data['minute'].iloc[0] if len(new_data) > 0 else None
    
    if latest_minute is not None and latest_minute not in stored_data['minute'].values:
        # Append new data
        updated_data = pd.concat([stored_data, new_data], ignore_index=True)
        
        # Sort by minute
        updated_data = updated_data.sort_values(['minute', 'rank'])
        
        # Store back to session state
        session_key = f"live_data_{team_name.replace(' ', '_')}"
        st.session_state[session_key] = updated_data
        
        return updated_data
    
    return stored_data

def clear_stored_live_data(team_name=None):
    """
    Clear stored live match data for a team or all teams
    
    Args:
        team_name: Name of the team to clear data for, or None to clear all
    """
    if team_name is None:
        # Clear all live data
        for key in list(st.session_state.keys()):
            if key.startswith('live_data_'):
                del st.session_state[key]
    else:
        # Clear just this team's data
        session_key = f"live_data_{team_name.replace(' ', '_')}"
        if session_key in st.session_state:
            del st.session_state[session_key]

def save_live_data_to_csv(team_name, opponent_name, data, directory="match_history"):
    """
    Save live match data to a CSV file
    
    Args:
        team_name: Name of the home team
        opponent_name: Name of the opponent team
        data: DataFrame containing live match data
        directory: Directory to save the file in
    """
    if data is None or data.empty:
        return
    
    # Create directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    # Create filename with team names and current date
    date_str = pd.Timestamp.now().strftime("%Y%m%d")
    filename = f"{directory}/{team_name.replace(' ', '_')}_vs_{opponent_name.replace(' ', '_')}_{date_str}.csv"
    
    # Save to CSV
    data.to_csv(filename, index=False)
    
    return filename