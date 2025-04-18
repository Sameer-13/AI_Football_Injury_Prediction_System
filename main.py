import streamlit as st
import os
from PIL import Image

from components.sidebar import display_team_selector
from components.table import display_player_table
from components.metric_plane import display_risk_summary

from utils.loader import load_data
from utils.config import LOGO_PATH
from utils.html_handler import logo_to_base64
from utils.df_loader import get_player_df

st.set_page_config(
    page_title="InjurySense.AI",
    page_icon="⚽",
    layout="wide"
)

# Display logo
if os.path.exists(LOGO_PATH):
    logo = Image.open(LOGO_PATH)
    st.markdown(
        f"""
        <div style="text-align: center;">
            <img src="data:image/png;base64,{logo_to_base64(logo)}" width="400">
        </div>
        """,
        unsafe_allow_html=True
    )
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
st.header(f"Team: Saudi Arabia National Football Team") # st.header(f"Team: {selected_team}")

# load player df
player_df = get_player_df(team_players)

# Display risk summary
display_risk_summary(player_df)

# Display player table with injury predictions
player_display_df = display_player_table(player_df)

