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
    
    # Get list of team names
    team_names = df_teams['team_name'].tolist() if not df_teams.empty else ["No teams available"]

    # Home team selection
    selected_team = st.sidebar.selectbox("Select your team:", team_names, index=0, key="home_team")
    
    # Display team logo if available
    if not df_teams.empty and selected_team in df_teams['team_name'].values:
        team_logo_url = df_teams[df_teams['team_name'] == selected_team]['logo'].values[0]
        st.sidebar.markdown(
            f"""
            <div style="text-align: center; margin-bottom: 1rem;">
                <img src="{team_logo_url}" width="100">
                <div style="color: #b0b0b0; margin-top: 0.5rem;">{selected_team}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Away team selection
    analysis_mode = st.session_state.get("analysis_mode", "Pre-Match Analysis")
    
    # Only show opponent selection in pre-match mode
    if analysis_mode == "Pre-Match Analysis":
        opponent_team = st.sidebar.selectbox("Select opponent team:", team_names, 
                                            index=min(1, len(team_names)-1) if len(team_names) > 1 else 0, 
                                            key="away_team")
        
        # Display opponent logo if available
        if not df_teams.empty and opponent_team in df_teams['team_name'].values:
            opponent_logo_url = df_teams[df_teams['team_name'] == opponent_team]['logo'].values[0]
            st.sidebar.markdown(
                f"""
                <div style="text-align: center; margin-bottom: 1rem;">
                    <img src="{opponent_logo_url}" width="100">
                    <div style="color: #b0b0b0; margin-top: 0.5rem;">{opponent_team}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        # In in-match mode, use the first team as opponent (placeholder)
        opponent_team = team_names[min(1, len(team_names)-1)] if len(team_names) > 1 else team_names[0]

    # Add division line
    st.sidebar.markdown("<hr>", unsafe_allow_html=True)

    # Add mode selector
    st.sidebar.markdown("<h2 style='text-align: center;'>Analysis Mode</h2>", unsafe_allow_html=True)
    analysis_mode = st.sidebar.radio(
        "Select Analysis Mode:", 
        ["Pre-Match Analysis", "In-Match Analysis"],
        index=0,
        key="analysis_mode"
    )
    
    # # Add mode description
    # if analysis_mode == "Pre-Match Analysis":
    #     st.sidebar.markdown(
    #         """
    #         <div style="background-color: #2C2F44; border-radius: 10px; padding: 1rem; margin-top: 1rem; font-size: 0.9rem;">
    #             <p style="margin: 0; color: #b0b0b0;">
    #                 Pre-match analysis provides injury risk predictions based on historical player data, workload, and fixture context.
    #             </p>
    #         </div>
    #         """,
    #         unsafe_allow_html=True
    #     )
    # else:
    #     st.sidebar.markdown(
    #         """
    #         <div style="background-color: #2C2F44; border-radius: 10px; padding: 1rem; margin-top: 1rem; font-size: 0.9rem;">
    #             <p style="margin: 0; color: #b0b0b0;">
    #                 In-match analysis provides real-time injury risk monitoring during live matches based on player performance metrics.
    #             </p>
    #         </div>
    #         """,
    #         unsafe_allow_html=True
    #     )
    
    # Add additional information for in-match mode
    # if analysis_mode == "In-Match Analysis":
    #     st.sidebar.markdown("<hr>", unsafe_allow_html=True)
    #     st.sidebar.markdown("<h3 style='text-align: center;'>Live Match Info</h3>", unsafe_allow_html=True)
        
    #     # Show mock data option for demonstration purposes
    #     st.sidebar.markdown(
    #         """
    #         <div style="background-color: #2C2F44; border-radius: 10px; padding: 1rem; margin-top: 1rem; font-size: 0.9rem;">
    #             <p style="margin: 0; color: #b0b0b0;">
    #                 If no live match is in progress, you can view a demonstration with simulated data.
    #             </p>
    #         </div>
    #         """,
    #         unsafe_allow_html=True
    #     )
    
    return selected_team, opponent_team