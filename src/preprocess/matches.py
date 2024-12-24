import pandas as pd

def preprocess_matches(all_matches):
    if not isinstance(all_matches, list) or not all_matches:
        return pd.DataFrame(columns=['_id', 'date', 'home_score_fulltime', 'away_score_fulltime'])

    matches_df = pd.DataFrame(all_matches)
    
    # Convert 'date' column to datetime format
    matches_df['date'] = pd.to_datetime(matches_df['date'], errors='coerce')
    if matches_df['date'].isna().any():
        print("Warning: Some dates could not be parsed and were set to NaT.")
    
    # Define stats_columns
    stats_columns = [
        'home_shots_total', 'home_shots_on_target', 'home_possession', 'home_passes_total', 
        'home_pass_completion', 'home_fouls_committed', 'home_corners', 'home_offsides_caught', 
        'away_shots_total', 'away_shots_on_target', 'away_possession', 'away_passes_total', 
        'away_pass_completion', 'away_fouls_committed', 'away_corners', 'away_offsides_caught'
    ]
    
    # Log missing values in columns
    for column in ['home_score_fulltime', 'away_score_fulltime'] + stats_columns:
        if matches_df[column].isna().any():
            print(f"Warning: Missing values found in {column}. Filling with default values.")
    
    # Convert score columns to integers and handle missing values
    score_columns = ['home_score_fulltime', 'away_score_fulltime']
    matches_df[score_columns] = matches_df[score_columns].fillna(0).astype(int)
    
    # Handle other columns (stats) by filling NaNs and converting to float
    matches_df[stats_columns] = matches_df[stats_columns].fillna(0).astype(float)
    
    return matches_df