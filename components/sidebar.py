import streamlit as st

def display_team_selector(df):
    """
    Display modern team selection interface in the sidebar
    with properly rendered upcoming match section
    
    Args:
        df: DataFrame containing team information
        
    Returns:
        str: Selected team name
    """
    st.sidebar.markdown(
        """
        <div style="text-align: center; margin-bottom: 2rem;">
            <h2 style="color: white; font-weight: 600; margin-bottom: 0;">Team Selection</h2>
            <div style="height: 3px; background: linear-gradient(90deg, #5762D5 0%, #4CAF50 100%); margin: 0.5rem auto; width: 50%;"></div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Get unique teams
    teams = df['team_name'].unique()
    
    # Create team selection dropdown with custom styling
    st.sidebar.markdown(
        """
        <style>
        div[data-baseweb="select"] {
            background-color: #2C2F44;
            border-radius: 10px;
            border: 1px solid #333545;
            padding: 0.5rem;
        }
        div[data-baseweb="select"] > div {
            background-color: transparent !important;
            border: none !important;
        }
        </style>
        <div style="padding: 0 1rem; margin-bottom: 1rem;">
            <label style="font-weight: 600; color: #b0b0b0; margin-bottom: 0.5rem; display: block;">Select  team:</label>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Create team selection dropdown
    selected_team = st.sidebar.selectbox(
        "",  # Empty label as we've added it with HTML
        options=teams,
        index=0,
        key="team_selection"
    )
    
    # Create opponent team selection dropdown with custom styling
    st.sidebar.markdown(
        """
        <style>
        div[data-baseweb="select"] {
            background-color: #2C2F44;
            border-radius: 10px;
            border: 1px solid #333545;
            padding: 0.5rem;
        }
        div[data-baseweb="select"] > div {
            background-color: transparent !important;
            border: none !important;
        }
        </style>
        <div style="padding: 0 1rem; margin-bottom: 1rem;">
            <label style="font-weight: 600; color: #b0b0b0; margin-bottom: 0.5rem; display: block;">Select the opponent team:</label>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Create opponent team selection dropdown
    opponent_selected_team = st.sidebar.selectbox(
        "",  # Empty label as we've added it with HTML
        options=teams,
        index=0,
        key="opponent_team_selection"
    )
    
    # Add separation line
    st.sidebar.markdown("<hr style='margin: 2rem 0; border-color: #333545;'>", unsafe_allow_html=True)
    
    # Add upcoming match section using Streamlit native components instead of HTML
    st.sidebar.subheader("Upcoming Match")
    
    # Create a container with styling for the match info
    with st.sidebar.container():
        # Use columns for team vs team layout
        col1, col2, col3 = st.sidebar.columns([2, 1, 2])
        
        with col1:
            st.write("**Team 155**")
        
        with col2:
            st.write("VS")
        
        with col3:
            st.write("**Team 201**")
        
        # Match date and time
        st.info("April 20, 2025 • 15:00")
    
    # Add filters section
    st.sidebar.markdown("<hr style='margin: 2rem 0; border-color: #333545;'>", unsafe_allow_html=True)
    st.sidebar.subheader("Filters")
    
    return selected_team