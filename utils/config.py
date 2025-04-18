# Configuration settings for the application

# File paths
DATA_PATH = r"C:\Users\smyra\Python Development\AI_Football_Injury_Prevention\data\cleaned_data.csv"
LOGO_PATH = r"C:\Users\smyra\Python Development\AI_Football_Injury_Prevention\assets\whiteLogo.png"

# Position mapping
POSITION_MAP = {
    1: "Goalkeeper",
    2: "Defender", 
    3: "Midfielder",
    4: "Forward",
}

# Column configurations
DISPLAY_COLUMNS = [
    'player_id', 
    'position', 
    'prev_player_age', 
    'prev_player_height', 
    'prev_player_weight',
    'prev_games_appearences', 
    'prev_games_minutes',
    'prev_games_rating', 
    'injuried'
]

COLUMN_RENAME_MAP = {
    'player_id': 'Player ID',
    'position': 'Position',
    'prev_player_age': 'Age',
    'prev_player_height': 'Height (cm)',
    'prev_player_weight': 'Weight (kg)',
    'prev_games_appearences': 'Appearances',
    'prev_games_minutes': 'Minutes Played',
    'prev_games_rating': 'Rating',
    'injuried': 'Injury Prediction'
}

# Styling configurations
HIGH_RISK_COLOR = 'red'
LOW_RISK_COLOR = 'green'