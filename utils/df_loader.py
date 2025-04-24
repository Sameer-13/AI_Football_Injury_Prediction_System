from utils.config import DISPLAY_COLUMNS, COLUMN_RENAME_MAP

def get_player_df(team_players):
    """
    Load and return the player DataFrame.
    
    Args:
        team_players: DataFrame containing player data for a specific team
        
    Returns:
        DataFrame: Player data with injury predictions
    """
    # Select columns for display
    player_display_df = team_players[DISPLAY_COLUMNS].copy()

    # Rename columns for display
    player_display_df = player_display_df.rename(columns=COLUMN_RENAME_MAP)

    # Add readable risk label
    player_display_df['Injury Risk'] = player_display_df['inj_probability'].apply(
        lambda x: 'High Risk' if x > 0.5 else 'Low Risk')
    
    return player_display_df