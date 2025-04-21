import streamlit as st

def display_team_selector(df_teams):
    """
    Display team and opponent selectors in sidebar using logos
    
    Args:
        df_teams: DataFrame with team_name and logo columns
        
    Returns:
        tuple: (selected_team_name, selected_opponent_name)
    """
    st.sidebar.markdown("<h2 style='text-align: center;'>Team Selection</h2>", unsafe_allow_html=True)
    
    team_names = df_teams['team_name'].tolist()

    selected_team = st.sidebar.selectbox("Select your team:", team_names, index=0, key="home_team")
    team_logo_url = df_teams[df_teams['team_name'] == selected_team]['logo'].values[0]
    st.sidebar.markdown(
    f"""
    <div style="text-align: center; margin-bottom: 1rem;">
        <img src="{team_logo_url}" width="100">
        <div style="color: #b0b0b0; margin-top: 0.5rem;">{selected_team} logo</div>
    </div>
    """,
    unsafe_allow_html=True
)

    opponent_team = st.sidebar.selectbox("Select opponent team:", team_names, index=1, key="away_team")    
    opponent_logo_url = df_teams[df_teams['team_name'] == opponent_team]['logo'].values[0]
    st.sidebar.markdown(
    f"""
    <div style="text-align: center; margin-bottom: 1rem;">
        <img src="{opponent_logo_url}" width="100">
        <div style="color: #b0b0b0; margin-top: 0.5rem;">{opponent_team} logo</div>
    </div>
    """,
    unsafe_allow_html=True
)

    # Optional: show upcoming match
    st.sidebar.markdown("<hr>", unsafe_allow_html=True)

    return selected_team, opponent_team
