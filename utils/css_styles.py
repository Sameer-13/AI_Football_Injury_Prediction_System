import streamlit as st

def load_general_styles():
    """
    Loads general styling for the entire application
    """
    st.markdown("""
    <style>
        /* Main container styling */
        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
        
        /* Card styling */
        div.css-1r6slb0.e1tzin5v2 {
            background-color: #1E2130;
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        /* Header styling */
        h1, h2, h3, h4 {
            color: #FFFFFF;
            font-weight: 600;
        }
        
        /* Table styling */
        div.stDataFrame {
            border-radius: 10px;
            overflow: hidden;
        }
        
        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            background-color: #1E2130;
            border-right: 1px solid #333545;
        }
        
        section[data-testid="stSidebar"] h1, 
        section[data-testid="stSidebar"] h2, 
        section[data-testid="stSidebar"] h3 {
            padding-left: 1rem;
        }
        
        section[data-testid="stSidebar"] .stSelectbox label {
            padding-left: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)

def load_metric_styles():
    """
    Loads styling for metric components
    """
    st.markdown("""
    <style>
        /* Metric card styling */
        div[data-testid="stMetricValue"] {
            font-size: 2.5rem !important;
            font-weight: 700 !important;
        }
        
        div[data-testid="stMetricDelta"] {
            font-size: 1rem !important;
        }
        
        div[data-testid="stMetricLabel"] {
            font-size: 1rem !important;
            font-weight: 600 !important;
        }
        
        /* Dashboard cards */
        .dashboard-card {
            background-color: #2C2F44;
            border-radius: 10px;
            padding: 1.5rem;
            height: 100%;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        /* Risk indicators */
        .high-risk-indicator {
            background-color: rgba(231, 76, 60, 0.9);
            color: white;
            border-radius: 5px;
            padding: 0.3rem 0.6rem;
            font-weight: 600;
            text-align: center;
        }
        
        .low-risk-indicator {
            background-color: rgba(93, 184, 92, 0.9);
            color: white;
            border-radius: 5px;
            padding: 0.3rem 0.6rem;
            font-weight: 600;
            text-align: center;
        }
    </style>
    """, unsafe_allow_html=True)

def load_player_card_styles():
    """
    Loads styling for player cards
    """
    st.markdown("""
    <style>
        /* Player spotlight */
        .player-spotlight {
            display: flex;
            align-items: center;
            margin-top: 1rem;
        }
        
        .player-avatar {
            width: 100px;
            height: 100px;
            border-radius: 50%;
            background-color: #3b3f5c;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 1.5rem;
            font-size: 2.5rem;
            color: white;
        }
        
        .player-info {
            flex-grow: 1;
        }
        
        .player-name {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        
        .player-stats {
            display: flex;
            gap: 1rem;
        }
        
        .stat-item {
            background-color: #3b3f5c;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            text-align: center;
        }
        
        .stat-value {
            font-size: 1.2rem;
            font-weight: 600;
        }
        
        .stat-label {
            font-size: 0.8rem;
            color: #b0b0b0;
        }
    </style>
    """, unsafe_allow_html=True)

def load_header_styles():
    """
    Loads styling for header and navigation components
    """
    st.markdown("""
    <style>
        /* Custom header */
        .header-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem 1rem;
            background-color: #1E2130;
            border-radius: 10px;
            margin-bottom: 1rem;
        }
        
        .header-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: #FFFFFF;
        }
        
        .header-actions button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            cursor: pointer;
            font-weight: 600;
        }
    </style>
    """, unsafe_allow_html=True)

def get_gradient_header(title, gradient_start="#5762D5", gradient_end="#4CAF50"):
    """
    Returns HTML for a gradient header
    
    Args:
        title: Header title text
        gradient_start: Starting gradient color
        gradient_end: Ending gradient color
        
    Returns:
        str: HTML string for the header
    """
    return f"""
    <div style="background: linear-gradient(90deg, {gradient_start} 0%, {gradient_end} 100%); padding: 1rem; border-radius: 10px; margin-bottom: 1.5rem;">
        <h2 style="color: white; margin: 0; font-weight: 600;">{title}</h2>
    </div>
    """

def get_section_header(title, gradient_start="#2C2F44", gradient_end="#1E2130"):
    """
    Returns HTML for a section header
    
    Args:
        title: Section title text
        gradient_start: Starting gradient color
        gradient_end: Ending gradient color
        
    Returns:
        str: HTML string for the section header
    """
    return f"""
    <div style="background: linear-gradient(90deg, {gradient_start} 0%, {gradient_end} 100%); padding: 1rem; border-radius: 10px; margin: 1.5rem 0;">
        <h3 style="color: white; margin: 0; font-weight: 600;">{title}</h3>
    </div>
    """

def get_high_risk_section_header(title):
    """
    Returns HTML for a high risk section header with red gradient
    
    Args:
        title: Section title text
        
    Returns:
        str: HTML string for the high risk section header
    """
    return get_section_header(title, "#E74C3C", "#922B21")

def get_dashboard_card_start():
    """
    Returns HTML for starting a dashboard card
    
    Returns:
        str: HTML string for starting a dashboard card
    """
    return """
    <div class="dashboard-card">
    """

def get_dashboard_card_end():
    """
    Returns HTML for ending a dashboard card
    
    Returns:
        str: HTML string for ending a dashboard card
    """
    return """
    </div>
    """

def get_footer():
    """
    Returns HTML for a footer
    
    Returns:
        str: HTML string for the footer
    """
    return """
    <div style="margin-top: 2rem; text-align: center; color: #b0b0b0; font-size: 0.8rem;">
        InjurySense.AI © 2025 | Powered by AI Football Injury Prevention System
    </div>
    """