import streamlit as st
import pandas as pd
from utils.config import DATA_PATH, POSITION_MAP, TEAMS_PATH

@st.cache_data
def load_data():
    """
    Load and preprocess data from CSV file
    
    Returns:
        DataFrame: Processed DataFrame with team and position information
    """
    try:
        # Load the dataset
        # df = pd.read_csv(DATA_PATH)
        df = pd.read_csv(r"C:\Users\smyra\Python Development\AI_Football_Injury_Prevention\data\pre_match_data\risk_Ohod_vs_Al_Khaleej_Saihat.csv")
        
        # # Convert position codes to names
        # if 'prev_games_position' in df.columns:
        #     df['position'] = df['prev_games_position'].map(POSITION_MAP)
        # else:
        #     df['position'] = "Not Specified"
        
        # # Extract team information from player IDs
        # if 'player_id' in df.columns:
        #     # Create team_id based on the first digits of player_id
        #     df['team_id'] = df['player_id'].astype(str).str[:3].astype(int)
            
        #     # Create team names based on team_id
        #     teams = {team_id: f"Team {team_id}" for team_id in df['team_id'].unique()}
        #     df['team_name'] = df['team_id'].map(teams)
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        # Return empty DataFrame if there's an error
        return pd.DataFrame(columns=['injuried', 'player_id', 'team_id', 'team_name', 'position'])


def load_teams_data():
    """
    Load and preprocess teams data from CSV file
    
    Returns:
        DataFrame: Processed DataFrame with team name, id, and logo
    """
    try:
        # Load the dataset
        df = pd.read_csv(TEAMS_PATH)

        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        # Return empty DataFrame if there's an error
        return pd.DataFrame(columns=['team_id', 'team_name', 'logo'])