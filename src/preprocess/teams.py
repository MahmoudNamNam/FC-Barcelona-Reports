import logging

import pandas as pd

def preprocess_teams(all_teams):
    logging.info("Starting to preprocess teams")
    
    teams_df = pd.DataFrame(all_teams).drop_duplicates(subset=['_id'])
    logging.info(f"Dropped duplicates, remaining teams: {len(teams_df)}")
    
    teams_df = teams_df[['_id', 'name', 'manager_name', 'competition']]
    
    # Checking if any critical columns are missing
    if teams_df['name'].isnull().any():
        logging.warning("There are missing team names.")
    
    teams_df['competition'] = teams_df['competition'].astype('category')
    logging.info("Finished preprocessing teams")
    
    return teams_df
