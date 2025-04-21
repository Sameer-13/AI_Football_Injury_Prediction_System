#!/usr/bin/env python3
# Check if a team has a live match
# Usage: python has_live_match.py "Team Name"
# Returns: 1 if team has a live match, 0 if not

import sys
import requests
import time

# API Config
API_KEY = "a945cc6862946161b617d75f42b12886"
BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {"x-rapidapi-host": "v3.football.api-sports.io",
           "x-rapidapi-key": API_KEY}

def api_get(endpoint, params):
    """Simple API wrapper with retry logic"""
    for attempt in range(3):
        try:
            r = requests.get(f"{BASE_URL}/{endpoint}", headers=HEADERS, params=params, timeout=10)
            if r.status_code == 429:  # Rate limited
                time.sleep(2)
                continue
            r.raise_for_status()
            return r.json().get("response", [])
        except Exception as e:
            if attempt < 2:
                time.sleep(1)
            else:
                print(f"API error: {e}", file=sys.stderr)
                return []
    return []

def find_team_id(team_name):
    """Find team ID from name"""
    teams = api_get("teams", {"search": team_name})
    if not teams:
        print(f"No team found for '{team_name}'", file=sys.stderr)
        return None
    return teams[0]["team"]["id"]

def has_live_match(team_id):
    """Check if team has a live match"""
    fixtures = api_get("fixtures", {"team": team_id, "live": "all"})
    return 1 if fixtures else 0

def main():
    # Check arguments
    if len(sys.argv) != 2:
        print("Usage: python has_live_match.py \"Team Name\"", file=sys.stderr)
        sys.exit(2)
    
    team_name = sys.argv[1]
    
    # Find team ID
    team_id = find_team_id(team_name)
    if not team_id:
        print(0)  # No team found, so no live match
        sys.exit(0)
    
    # Check for live match
    result = has_live_match(team_id)
    
    # Print the result (1 for yes, 0 for no)
    print(result)

if __name__ == "__main__":
    main()