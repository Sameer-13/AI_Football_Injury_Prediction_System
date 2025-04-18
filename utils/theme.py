import streamlit as st

def apply_custom_theme():
    """
    Apply custom theme settings for the Streamlit app
    """
    # Set theme colors
    st.markdown("""
    <style>
        :root {
            --primary-color: #5762D5;
            --secondary-color: #4CAF50;
            --accent-color: #E74C3C;
            --warning-color: #F1C40F;
            --info-color: #3498DB;
            
            --background-color: #121526;
            --secondary-background-color: #1E2130;
            --card-background-color: #2C2F44;
            --hover-background-color: #3b3f5c;
            
            --text-color: #FFFFFF;
            --secondary-text-color: #B0B0B0;
            
            --border-color: #333545;
            --border-radius: 10px;
            --box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        /* Main app background */
        .stApp {
            background-color: var(--background-color);
        }
        
        /* Text colors */
        p, span, label, div:not(.high-risk-indicator):not(.low-risk-indicator) {
            color: var(--text-color) !important;
        }
        
        /* Button styling */
        .stButton>button {
            background-color: var(--primary-color);
            color: var(--text-color);
            border-radius: 5px;
            border: none;
            padding: 0.5rem 1rem;
            font-weight: 600;
        }
        
        .stButton>button:hover {
            background-color: #4855C4;
            color: var(--text-color);
        }
        
        /* Select box styling */
        .stSelectbox>div>div {
            background-color: var(--secondary-background-color);
            color: var(--text-color);
            border-radius: 5px;
            border: 1px solid var(--border-color);
        }
        
        /* Metric styling */
        [data-testid="stMetric"] {
            background-color: var(--secondary-background-color);
            border-radius: var(--border-radius);
            padding: 1rem;
            box-shadow: var(--box-shadow);
        }
        
        [data-testid="stMetricValue"] {
            color: var(--text-color) !important;
        }
        
        /* Multi-select */
        .stMultiSelect>div>div {
            background-color: var(--secondary-background-color);
            border: 1px solid var(--border-color);
        }
        
        /* Radio buttons */
        .stRadio>div {
            background-color: var(--secondary-background-color);
            border-radius: var(--border-radius);
            padding: 1rem;
        }
        
        /* Data frame */
        .stDataFrame {
            background-color: var(--card-background-color);
            border-radius: var(--border-radius);
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            background-color: var(--secondary-background-color);
            border-radius: var(--border-radius);
        }
        
        .stTabs [data-baseweb="tab"] {
            color: var(--text-color);
        }
        
        .stTabs [aria-selected="true"] {
            background-color: var(--primary-color);
        }
    </style>
    """, unsafe_allow_html=True)