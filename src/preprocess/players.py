import logging
import pandas as pd

# Set up logger
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

def preprocess_players(all_player_stats):
    if not isinstance(all_player_stats, list) or not all_player_stats:
        logger.warning("Input is not a valid list or is empty.")
        return pd.DataFrame(columns=['_id', 'name', 'shirt_no', 'position', 'age', 'team_id', 'stats', 'competition', 'match_id'])
    
    players_df = pd.DataFrame(all_player_stats)
    
    # Check for missing columns
    required_columns = ['_id', 'name', 'shirt_no', 'position', 'age', 'team_id', 'stats', 'competition', 'match_id']
    missing_columns = [col for col in required_columns if col not in players_df.columns]
    if missing_columns:
        logger.warning(f"Missing columns: {', '.join(missing_columns)}")
    
    # Processing columns and logging at each stage
    players_df['name'] = players_df['name'].fillna('Unknown Player')
    players_df['team_id'] = players_df['team_id'].fillna(0).astype(int)
    players_df['age'] = players_df['age'].fillna(0).astype(int)
    players_df['shirt_no'] = players_df['shirt_no'].fillna(0).astype(int)
    players_df['position'] = players_df['position'].astype('category')
    players_df['competition'] = players_df['competition'].astype('category')

    # Log the completion of preprocessing
    logger.info("Player data preprocessing completed successfully.")
    
    return players_df
