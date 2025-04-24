#!/usr/bin/env python3
# Live Rank Script - Maps individual player stats to model features and saves risk rankings
# Usage: python live_rank_script.py "Team Name"

import sys
import requests
import pandas as pd
import numpy as np
import joblib
import time
import os

# Config
API_KEY = "a945cc6862946161b617d75f42b12886"
BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {"x-rapidapi-host": "v3.football.api-sports.io",
           "x-rapidapi-key": API_KEY}

MODEL_PATH = "best_survival_model.pkl"  # Path to your model
OUT_CSV = "live_risk_rankings.csv"

# Original model features
ORIGINAL_FEATURES = [
    'shots_on_goal_cum', 
    'shots_off_goal_cum',
    'total_shots_cum', 
    'blocked_shots_cum', 
    'shots_insidebox_cum',
    'shots_outsidebox_cum', 
    'fouls_cum', 
    'corner_kicks_cum', 
    'offsides_cum',
    'yellow_cards_cum', 
    'goalkeeper_saves_cum', 
    'total_passes_cum',
    'passes_accurate_cum', 
    'goals_prevented_cum', 
    'red_cards_cum'
]

# API Helper Function
def api_get(endpoint, params):
    """Simple API wrapper"""
    for attempt in range(3):
        try:
            r = requests.get(f"{BASE_URL}/{endpoint}", headers=HEADERS, params=params, timeout=10)
            if r.status_code == 429:  # Rate limited
                print(f"Rate limited. Waiting before retry...")
                time.sleep(2)
                continue
            r.raise_for_status()
            return r.json().get("response", [])
        except Exception as e:
            print(f"API error: {e}")
            if attempt < 2:
                print("Retrying...")
            else:
                print("All retries failed.")
                raise
    return []

def find_team_id(team_name):
    """Find team ID from name"""
    teams = api_get("teams", {"search": team_name})
    if not teams:
        raise ValueError(f"No team found for '{team_name}'")
    return teams[0]["team"]["id"]

def find_live_fixture(team_id):
    """Find live fixture for a team"""
    fixtures = api_get("fixtures", {"team": team_id, "live": "all"})
    if not fixtures:
        raise ValueError(f"No LIVE fixture found for team {team_id}")
    return fixtures[0]["fixture"]["id"]

def get_team_stats(fixture_id, team_id):
    """Get team statistics"""
    stats_blocks = api_get("fixtures/statistics", {"fixture": fixture_id})
    for blk in stats_blocks:
        if blk["team"]["id"] == team_id:
            stats = {}
            for s in blk["statistics"]:
                key = s["type"].lower().replace(" ", "_") + "_cum"
                value = s["value"]
                
                # Convert string percentages to floats
                if isinstance(value, str) and '%' in value:
                    value = float(value.replace('%', '')) / 100
                
                # Convert string numbers to float/int
                if isinstance(value, str) and value.replace('.', '', 1).isdigit():
                    value = float(value)
                
                # Only keep numeric values
                if isinstance(value, (int, float)):
                    stats[key] = value
            
            return stats
    return {}

def get_players_on_pitch(fixture_id, team_id):
    """Get player IDs of all players in the squad"""
    lineups = api_get("fixtures/lineups", {"fixture": fixture_id})
    for lu in lineups:
        if lu["team"]["id"] != team_id:
            continue
        players = lu["startXI"] + lu["substitutes"]
        return [p["player"]["id"] for p in players]
    return []

def get_player_names(fixture_id, team_id):
    """Get player names from lineup data"""
    player_names = {}
    lineups = api_get("fixtures/lineups", {"fixture": fixture_id})
    for lu in lineups:
        if lu["team"]["id"] != team_id:
            continue
        for p in lu["startXI"] + lu["substitutes"]:
            player_id = p["player"]["id"]
            player_name = p["player"].get("name", f"ID: {player_id}")
            player_names[player_id] = player_name
    return player_names

def get_current_minute(fixture_id):
    """Get current match minute"""
    info = api_get("fixtures", {"id": fixture_id})
    if info:
        return info[0]["fixture"]["status"]["elapsed"] or 0
    return 0

def get_player_specific_stats(fixture_id, team_id):
    """Get individual player statistics and map them to model features"""
    player_stats = api_get("fixtures/players", {"fixture": fixture_id, "team": team_id})
    
    if not player_stats or len(player_stats) == 0 or "players" not in player_stats[0]:
        print("No player statistics available from API")
        return {}
    
    # Get team totals for context
    team_stats = get_team_stats(fixture_id, team_id)
    
    # Process player stats and map to original features
    mapped_stats = {}
    for player in player_stats[0]["players"]:
        player_id = player["player"]["id"]
        stats = player["statistics"][0]
        
        # Create a mapping structure for this player
        player_features = {}
        
        # --- MAP PLAYER INDIVIDUAL STATS TO MODEL FEATURES ---
        
        # 1. Shots mapping
        if "shots" in stats:
            player_features["shots_on_goal_cum"] = stats["shots"].get("on", 0) or 0
            
            # Total shots minus on-target = off-target
            total_shots = stats["shots"].get("total", 0) or 0
            on_target = stats["shots"].get("on", 0) or 0
            player_features["shots_off_goal_cum"] = max(0, total_shots - on_target)
            
            player_features["total_shots_cum"] = total_shots
            
            # No direct mapping for blocked shots, inside/outside box
            # We'll estimate these based on team proportions later
        
        # 2. Fouls mapping
        if "fouls" in stats:
            player_features["fouls_cum"] = stats["fouls"].get("committed", 0) or 0
        
        # 3. No direct mapping for corner_kicks_cum
        
        # 4. Offsides mapping
        player_features["offsides_cum"] = stats.get("offsides", 0) or 0
        
        # 5. Cards mapping
        if "cards" in stats:
            player_features["yellow_cards_cum"] = stats["cards"].get("yellow", 0) or 0
            player_features["red_cards_cum"] = stats["cards"].get("red", 0) or 0
        
        # 6. Goalkeeper saves
        if "goals" in stats:
            player_features["goalkeeper_saves_cum"] = stats["goals"].get("saves", 0) or 0
        
        # 7. Passes mapping
        if "passes" in stats:
            player_features["total_passes_cum"] = stats["passes"].get("total", 0) or 0
            
            # Extract accuracy as a number without % sign
            accuracy = stats["passes"].get("accuracy", None)
            if accuracy is not None:
                # Convert to float if it's a string
                if isinstance(accuracy, str):
                    try:
                        accuracy = float(accuracy.rstrip('%'))
                    except ValueError:
                        accuracy = 0
                
                # Now use the numeric accuracy
                if isinstance(accuracy, (int, float)) and accuracy > 0 and player_features["total_passes_cum"] > 0:
                    player_features["passes_accurate_cum"] = int(player_features["total_passes_cum"] * (accuracy / 100))
                else:
                    player_features["passes_accurate_cum"] = 0
            else:
                player_features["passes_accurate_cum"] = 0
        
        # 8. No direct mapping for goals_prevented_cum
        
        # Save mapped features for this player
        mapped_stats[player_id] = player_features
    
    # Go through each player and fill in missing features
    for player_id, features in mapped_stats.items():
        # Fill in any missing original features
        for feature in ORIGINAL_FEATURES:
            if feature not in features:
                features[feature] = 0
        
        # Special case: Estimate shots distribution (blocked, inside/outside box)
        # based on team proportions
        if team_stats.get("total_shots_cum", 0) > 0 and features["total_shots_cum"] > 0:
            total_ratio = features["total_shots_cum"] / team_stats["total_shots_cum"]
            
            # Blocked shots estimate
            if "blocked_shots_cum" in team_stats:
                features["blocked_shots_cum"] = total_ratio * team_stats["blocked_shots_cum"]
            
            # Inside/outside box estimates
            if "shots_insidebox_cum" in team_stats:
                features["shots_insidebox_cum"] = total_ratio * team_stats["shots_insidebox_cum"]
            
            if "shots_outsidebox_cum" in team_stats:
                features["shots_outsidebox_cum"] = total_ratio * team_stats["shots_outsidebox_cum"]
        
        # Look up the current player object
        current_player = None
        for p in player_stats[0]["players"]:
            if p["player"]["id"] == player_id:
                current_player = p
                break
                
        # Special case: Estimate goals prevented for goalkeepers
        if current_player and "games" in current_player["statistics"][0] and current_player["statistics"][0]["games"].get("position") == "G":
            features["goals_prevented_cum"] = team_stats.get("goals_prevented_cum", 0)
    
    return mapped_stats

def build_player_dataframe(fixture_id, team_id):
    """Build dataframe with mapped individual player stats to model features"""
    # Get necessary data
    minute_now = get_current_minute(fixture_id)
    player_ids = get_players_on_pitch(fixture_id, team_id)
    team_stats = get_team_stats(fixture_id, team_id)
    player_stats = get_player_specific_stats(fixture_id, team_id)
    
    # Check if we have team stats
    if not team_stats:
        raise ValueError("No team statistics available - match may not have started")
    
    # Build rows for each player
    rows = []
    for pid in player_ids:
        # Create base row
        row = {
            "player_id": pid,
            "team_id": team_id,
            "fixture_id": fixture_id,
            "minute": minute_now
        }
        
        # Add player-specific features if available
        if pid in player_stats:
            for feature, value in player_stats[pid].items():
                row[feature] = value
        else:
            # If no player stats available, use small fraction of team stats
            for feature in ORIGINAL_FEATURES:
                row[feature] = 0.05 * team_stats.get(feature, 0)  # Assign 5% of team stats
        
        # Ensure all required features are present
        for feature in ORIGINAL_FEATURES:
            if feature not in row:
                row[feature] = 0
        
        rows.append(row)
    
    df = pd.DataFrame(rows)
    return df

def run_analysis(team_name=None, team_id=None, fixture_id=None, output_file=None):
    """Run the risk analysis using mapped player features and save to file"""
    # Set output file
    out_file = OUT_CSV
    
    # Get team ID
    if team_name and not team_id:
        print(f"Looking up team: {team_name}")
        team_id = find_team_id(team_name)
    
    if not team_id:
        raise ValueError("Team ID or name is required")
    
    # Get fixture ID
    if not fixture_id:
        print(f"Finding live fixture for team ID: {team_id}")
        fixture_id = find_live_fixture(team_id)
    
    print(f"Analyzing fixture {fixture_id} for team {team_id}")
    
    # Get player data with mapped features
    print("Mapping individual player statistics to model features...")
    player_df = build_player_dataframe(fixture_id, team_id)
    player_names = get_player_names(fixture_id, team_id)
    
    # Extract only the original features for the model
    feature_df = player_df[ORIGINAL_FEATURES].copy()
    
    # Make sure all values are numeric
    for col in feature_df.columns:
        feature_df[col] = pd.to_numeric(feature_df[col], errors='coerce').fillna(0)
    
    # Load model and predict
    print(f"Loading model from: {MODEL_PATH}")
    pipe = joblib.load(MODEL_PATH)
    
    # Predict risk scores
    print("Predicting risk scores using mapped player features...")
    player_df["risk_score"] = pipe.predict(feature_df)
    
    # Sort by risk score and add rank
    player_df = player_df.sort_values("risk_score", ascending=False)
    player_df["rank"] = range(1, len(player_df) + 1)
    
    # Add player names
    player_df["player_name"] = player_df["player_id"].map(player_names.get)
    
    # Save results
    player_df[["minute","player_name","risk_score","rank"]].to_csv(out_file, index=False)
    print(f"✅ Saved risk rankings to {out_file}")
    
    return player_df

def main():
    # Check arguments
    if len(sys.argv) < 2:
        print("Usage: python live_rank_script.py \"Team Name\" [output_file.csv]")
        sys.exit(1)
    
    team_name = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else OUT_CSV
    
    try:
        run_analysis(team_name=team_name, output_file=output_file)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()