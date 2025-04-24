import streamlit as st
import os
from PIL import Image
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="InjurySense.AI",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

from components.sidebar import display_team_selector
from components.table import display_player_table, plot_risk_dots_with_ci
from components.metric_plane import display_risk_summary
from components.player_cards import display_player_cards
from components.risk_charts import display_risk_charts
from components.in_match_analysis import display_in_match_analysis

from utils.loader import load_data, load_teams_data
from utils.config import LOGO_PATH
from utils.html_handler import logo_to_base64
from utils.df_loader import get_player_df
from utils.theme import apply_custom_theme
from utils.css_styles import (
    load_general_styles, 
    load_metric_styles, 
    load_player_card_styles, 
    load_header_styles,
    get_gradient_header,
    get_section_header,
    get_high_risk_section_header,
    get_dashboard_card_start,
    get_dashboard_card_end,
    get_footer
)

# Apply custom theme
apply_custom_theme()

# Load CSS styles
load_general_styles()
load_metric_styles()
load_player_card_styles()
load_header_styles()

# Header with logo and actions
col1, col2 = st.columns([6, 1])
with col1:
    # Display logo
    if os.path.exists(LOGO_PATH):
        logo = Image.open(LOGO_PATH)
        st.markdown(
            f"""
            <div style="text-align: left; margin-bottom: 1rem;">
                <img src="data:image/png;base64,{logo_to_base64(logo)}" width="250">
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.warning(f"Logo file not found. Please check the path in config.yaml: {LOGO_PATH}")

# Load teams data
teams_df = load_teams_data()

# Display team selector and mode toggle in sidebar
selected_team, opponent_team = display_team_selector(teams_df)

# Main content area
if st.session_state.get("analysis_mode", "Pre-Match Analysis") == "Pre-Match Analysis":
    # Pre-match mode
    st.markdown(get_gradient_header("Pre-Match Player Injury Prediction Dashboard"), unsafe_allow_html=True)
    
    # Load pre-match data
    players_df = load_data()
    
    # Team header with gradient background
    st.markdown(get_section_header(f"Team: {selected_team} vs {opponent_team}"), unsafe_allow_html=True)
    
    # Load player dataframe
    player_df = get_player_df(players_df)
    
    # Summary cards
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.markdown("<h4 style='margin-top: 0;'>Team Risk Overview</h4>", unsafe_allow_html=True)
        display_risk_summary(player_df)
        st.markdown(get_dashboard_card_end(), unsafe_allow_html=True)
    
    with col2:
        # Risk distribution chart
        st.markdown("<h4 style='margin-top: 0;'>Risk Distribution by Position</h4>", unsafe_allow_html=True)
        display_risk_charts(player_df)
        st.markdown(get_dashboard_card_end(), unsafe_allow_html=True)
    
    # High-risk players spotlight
    high_risk_players = player_df[player_df['inj_probability'] > 0.5]
    high_risk_count = len(high_risk_players)
    
    # Display player cards for high-risk players
    if high_risk_count > 0:
        st.markdown(
            get_high_risk_section_header("High Risk Players - Immediate Attention Required"),
            unsafe_allow_html=True
        )
        display_player_cards(high_risk_players)
    
    # Display player table with injury predictions
    st.markdown(get_section_header("Player Injury Risk Assessment"), unsafe_allow_html=True)
    plot_risk_dots_with_ci(player_df)

else:
    # In-match mode
    st.markdown(get_gradient_header("In-Match Live Injury Risk Monitoring"), unsafe_allow_html=True)
    
    # Use the dedicated in-match analysis component
    display_in_match_analysis(selected_team, opponent_team)

# Footer
st.markdown(get_footer(), unsafe_allow_html=True)
