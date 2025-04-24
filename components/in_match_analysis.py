import streamlit as st
from utils.in_match_utils import check_live_match, get_live_match_data, create_mock_live_data
from components.live_match_visualization import display_live_match_visualization
from utils.css_styles import get_section_header
import time

def display_in_match_analysis(selected_team, opponent_team):
    """
    Display the in-match analysis page
    
    Args:
        selected_team: Name of the selected team
        opponent_team: Name of the opponent team
    """
    st.markdown(get_section_header(f"Team: {selected_team}"), unsafe_allow_html=True)
    
    # Check if the selected team has a live match
    has_live_match = check_live_match(selected_team)
    
    if has_live_match:
        st.markdown(
            f"""
            <div style="background-color: #1E2130; border-radius: 10px; padding: 1rem; margin-bottom: 1rem;">
                <h3 style="margin: 0; color: #5DB85C;">
                    <span style="font-size: 1.5rem; margin-right: 0.5rem;">●</span> 
                    Live Match in Progress
                </h3>
                <p style="margin: 0.5rem 0 0 0; color: #b0b0b0;">
                    Real-time injury risk monitoring for {selected_team} is available.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Add refresh button
        col1, col2 = st.columns([6, 1])
        with col2:
            refresh = st.button("Refresh Data", key="refresh_button")
        
        # Get live match data
        live_data = get_live_match_data(selected_team, refresh=refresh)
        
        if live_data is not None and not live_data.empty:
            # Show current minute
            current_minute = live_data['minute'].iloc[0] if 'minute' in live_data.columns else "N/A"
            
            st.markdown(
                f"""
                <div style="background-color: #2C2F44; border-radius: 10px; padding: 1rem; margin-bottom: 1rem; text-align: center;">
                    <h2 style="margin: 0; color: white;">
                        Match Minute: {current_minute}'
                    </h2>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Show auto-refresh option
            auto_refresh = st.checkbox("Enable auto-refresh (every 60 seconds)", value=False)
            if auto_refresh:
                st.info("Auto-refresh is enabled. Data will update every 60 seconds.")
                time.sleep(60)
                st.experimental_rerun()
            
            # Display live match visualization
            display_live_match_visualization(live_data)
        else:
            st.warning("No live match data available. Try refreshing the data.")
    
    else:
        # st.warning(
        #     f"""
        #     No live match is currently in progress for {selected_team}.
            
        #     The in-match analysis is only available during live matches. Please check back during the team's next match,
        #     or switch to Pre-Match Analysis mode to view injury predictions for the upcoming matches.
        #     """
        # )
        
        # # Mock data for demonstration
        # if st.checkbox("Show demonstration with mock data", value=False):
        #     st.info("This is demonstration data and does not represent a real match.")
            
            # # Create mock live match data
            # mock_data = create_mock_live_data()
            # display_live_match_visualization(mock_data)
        mock_data = create_mock_live_data()
        display_live_match_visualization(mock_data)