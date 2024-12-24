import logging
from preprocess_matches import preprocess_matches
from preprocess_teams import preprocess_teams
from preprocess_players import preprocess_players
from preprocess_events import preprocess_events

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def preprocess_data(all_matches, all_teams, all_player_stats, all_events):
    """
    Preprocess raw match, team, player, and event data.

    This function applies preprocessing pipelines to multiple datasets by calling dedicated
    preprocessing functions for each data type. It standardizes, cleans, and transforms the
    data for further analysis or modeling.

    Args:
        all_matches (list): Raw match data in dictionary format.
        all_teams (list): Raw team data in dictionary format.
        all_player_stats (list): Raw player statistics data in dictionary format.
        all_events (list): Raw event data in dictionary format.

    Returns:
        tuple: A tuple containing four pandas DataFrames:
            - matches_df: Preprocessed match data.
            - teams_df: Preprocessed team data.
            - players_df: Preprocessed player statistics data.
            - events_df: Preprocessed event data.
    """
    logger.info("Starting data preprocessing...")

    logger.info("Preprocessing match data...")
    matches_df = preprocess_matches(all_matches)
    logger.info("Match data preprocessing complete.")

    logger.info("Preprocessing team data...")
    teams_df = preprocess_teams(all_teams)
    logger.info("Team data preprocessing complete.")

    logger.info("Preprocessing player statistics data...")
    players_df = preprocess_players(all_player_stats)
    logger.info("Player statistics data preprocessing complete.")

    logger.info("Preprocessing event data...")
    events_df = preprocess_events(all_events)
    logger.info("Event data preprocessing complete.")

    logger.info("All data preprocessing completed successfully.")
    
    return matches_df, teams_df, players_df, events_df
