import streamlit as st

def display_team_selector(df):
    """
    Display team selection dropdown in the sidebar
    
    Args:
        df: DataFrame containing team information
        
    Returns:
        str: Selected team name
    """
    st.sidebar.header("Team Selection")
    
    # Get unique teams
    teams = df['team_name'].unique()
    
    # Create team selection dropdown
    selected_team = st.sidebar.selectbox(
        "Select a team:",
        options=teams,
        index=0,
        key="team_selection"
    )
    
    return selected_team