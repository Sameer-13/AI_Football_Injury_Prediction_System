import streamlit as st
import os
from PIL import Image

# Import components
from components.sidebar import display_team_selector
from components.table import display_player_table
from components.metric_plane import display_risk_summary

# Import utilities
from utils.loader import load_data
from utils.config import LOGO_PATH

# Set page configuration
st.set_page_config(
    page_title="Football Injury Prediction System",
    page_icon="⚽",
    layout="wide"
)

# Display logo
if os.path.exists(LOGO_PATH):
    logo = Image.open(LOGO_PATH)
    st.image(logo, width=400)
else:
    st.warning("Logo file not found. Please check the path in config.py.")

# Page title and header
st.markdown("### Pre-Match Player Injury Prediction Dashboard")

# Load data
df = load_data()

# Display team selector in sidebar
selected_team = display_team_selector(df)

# Filter players by selected team
team_players = df[df['team_name'] == selected_team].copy()

# Display team information
st.header(f"Team: {selected_team}")

# Display player table with injury predictions
player_display_df = display_player_table(team_players)

# Display risk summary
display_risk_summary(player_display_df)