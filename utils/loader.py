import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    """
    Load and preprocess data from CSV file
    
    Returns:
        DataFrame: Processed DataFrame with team and position information
    """
    try:
        # Load the dataset
        df = pd.read_csv(r"C:\Users\smyra\Python Development\AI_Football_Injury_Prevention\data\cleaned_data.csv")
        
        # Map position codes to position names
        position_map = {
            1: "Goalkeeper",
            2: "Defender", 
            3: "Midfielder",
            4: "Forward",
        }
        
        # Convert position codes to names
        if 'prev_games_position' in df.columns:
            df['position'] = df['prev_games_position'].map(position_map)
        else:
            df['position'] = "Not Specified"
        
        # Extract team information from player IDs
        if 'player_id' in df.columns:
            # Create team_id based on the first digits of player_id
            df['team_id'] = df['player_id'].astype(str).str[:3].astype(int)
            
            # Create team names based on team_id
            teams = {team_id: f"Team {team_id}" for team_id in df['team_id'].unique()}
            df['team_name'] = df['team_id'].map(teams)
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        # Return empty DataFrame if there's an error
        return pd.DataFrame(columns=['injuried', 'player_id', 'team_id', 'team_name', 'position'])