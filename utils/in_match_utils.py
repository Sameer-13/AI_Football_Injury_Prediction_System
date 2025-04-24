import streamlit as st
import subprocess
import pandas as pd
import numpy as np
import os
import time

def check_live_match(team_name):
    """
    Check if a team has a live match in progress
    
    Args:
        team_name: Name of the team to check
        
    Returns:
        bool: True if team has a live match, False otherwise
    """
    try:
        result = subprocess.run(
            ["python", "model_inferences/in_match_inference/has_live_match.py", team_name], 
            capture_output=True, 
            text=True, 
            check=True
        )
        return int(result.stdout.strip()) == 1
    except Exception as e:
        st.error(f"Error checking live match: {e}")
        return False

def get_live_match_data(team_name, refresh=False):
    """
    Get live match risk data for a team
    
    Args:
        team_name: Name of the team to get data for
        refresh: Whether to force refresh the data
        
    Returns:
        DataFrame: Live match risk data
    """
    output_file = "live_risk_rankings.csv"
    
    try:
        # Run the analysis script
        if refresh:
            st.info("Updating live match data...")
            subprocess.run(
                ["python", "model_inferences/in_match_inference/live_rank_script.py", team_name, output_file], 
                check=True
            )
        
        # Load the output file
        if os.path.exists(output_file):
            return pd.read_csv(output_file)
        else:
            st.warning(f"No live match data file found: {output_file}")
            return None
    except Exception as e:
        st.error(f"Error getting live match data: {e}")
        return None

def create_mock_live_data():
    """
    Create realistic mock data for demonstration purposes
    
    Returns:
        DataFrame: Mock live match data with player risk rankings
    """
    # Create a sample dataset with multiple timestamps
    timestamps = [15, 30, 45, 60, 75, 90]
    players = [
        "Marcus Johnson", "Carlos Rivera", "Alex Chen", 
        "Ibrahim Diallo", "James Wilson", "Luka Novak", 
        "Thomas Müller", "Pedro Santos", "Kevin Lee", 
        "David Smith", "Mohammed Al-Fayez"
    ]
    
    # Player position mapping for more realistic data
    positions = {
        "Marcus Johnson": "Forward",
        "Carlos Rivera": "Midfielder",
        "Alex Chen": "Defender",
        "Ibrahim Diallo": "Midfielder",
        "James Wilson": "Forward",
        "Luka Novak": "Defender",
        "Thomas Müller": "Midfielder",
        "Pedro Santos": "Forward",
        "Kevin Lee": "Goalkeeper",
        "David Smith": "Defender",
        "Mohammed Al-Fayez": "Midfielder"
    }
    
    # Initial risk profiles - some players start higher risk
    initial_risk = {
        "Marcus Johnson": 0.75,  # High intensity forward
        "Carlos Rivera": 0.65,   # Box-to-box midfielder
        "Alex Chen": 0.45,       # Defender
        "Ibrahim Diallo": 0.60,  # Midfielder
        "James Wilson": 0.70,    # Forward
        "Luka Novak": 0.50,      # Defender
        "Thomas Müller": 0.55,   # Midfielder
        "Pedro Santos": 0.80,    # Forward with previous injury
        "Kevin Lee": 0.30,       # Goalkeeper
        "David Smith": 0.40,     # Defender
        "Mohammed Al-Fayez": 0.65 # Midfielder
    }
    
    # Risk progression patterns - some increase more over time
    risk_progression = {
        "Marcus Johnson": 0.03,   # Increases risk quickly
        "Carlos Rivera": 0.02,    # Moderate increase
        "Alex Chen": 0.01,        # Slow increase
        "Ibrahim Diallo": 0.025,  # Moderate increase
        "James Wilson": 0.035,    # Fast increase
        "Luka Novak": 0.015,      # Slow increase
        "Thomas Müller": 0.02,    # Moderate increase
        "Pedro Santos": 0.04,     # Fastest increase (previous injury)
        "Kevin Lee": 0.005,       # Very slow (goalkeeper)
        "David Smith": 0.01,      # Slow increase
        "Mohammed Al-Fayez": 0.025 # Moderate increase
    }
    
    # Random variation for each player
    variation_scale = {
        "Marcus Johnson": 0.07,    # High variation
        "Carlos Rivera": 0.05,     # Medium variation
        "Alex Chen": 0.04,         # Low-medium variation
        "Ibrahim Diallo": 0.06,    # Medium-high variation
        "James Wilson": 0.07,      # High variation
        "Luka Novak": 0.03,        # Low variation
        "Thomas Müller": 0.05,     # Medium variation
        "Pedro Santos": 0.08,      # Highest variation
        "Kevin Lee": 0.02,         # Very low variation
        "David Smith": 0.04,       # Low-medium variation
        "Mohammed Al-Fayez": 0.05  # Medium variation
    }
    
    data_rows = []
    
    # Add a special event - player gets a spike in risk at minute 60
    spike_player = "Marcus Johnson"
    spike_minute = 60
    
    for minute in timestamps:
        player_risks = {}
        
        # Calculate risk scores for this minute
        for player in players:
            # Calculate base risk with progression
            time_factor = minute / 90.0  # Match progression factor
            base_risk = initial_risk[player] + (risk_progression[player] * minute)
            
            # Add random variation
            variation = np.random.normal(0, variation_scale[player])
            
            # Add spike for specific player at specific minute
            spike = 0.15 if player == spike_player and minute == spike_minute else 0
            
            # Calculate final risk score and clamp to 0-1
            risk_score = min(max(base_risk + variation + spike, 0), 1)
            
            player_risks[player] = risk_score
        
        # Sort players by risk score to determine ranks
        sorted_players = sorted(player_risks.items(), key=lambda x: x[1], reverse=True)
        
        # Create data rows with ranks
        for rank, (player, risk_score) in enumerate(sorted_players, 1):
            data_rows.append({
                "minute": minute,
                "player_name": player,
                "position": positions[player],
                "risk_score": risk_score,
                "rank": rank
            })
    
    return pd.DataFrame(data_rows)