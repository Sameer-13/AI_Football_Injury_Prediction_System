def get_player_df (team_players):
    """
    Load and return the player DataFrame.
    
    Returns:
        DataFrame: Player data with injury predictions
    """
    # Select columns for display
    player_display_df = team_players[['player_id', 'position', 'prev_player_age', 
                                      'prev_player_height', 'prev_player_weight',
                                      'prev_games_appearences', 'prev_games_minutes',
                                      'prev_games_rating', 'injuried']].copy()

    # Rename columns for display
    player_display_df = player_display_df.rename(columns={
        'player_id': 'Player ID',
        'position': 'Position',
        'prev_player_age': 'Age',
        'prev_player_height': 'Height (cm)',
        'prev_player_weight': 'Weight (kg)',
        'prev_games_appearences': 'Appearances',
        'prev_games_minutes': 'Minutes Played',
        'prev_games_rating': 'Rating',
        'injuried': 'Injury Prediction'
    })

    # Add readable risk label
    player_display_df['Injury Risk'] = player_display_df['Injury Prediction'].apply(
        lambda x: 'High Risk' if x == 1 else 'Low Risk'
    )
    
    return player_display_df