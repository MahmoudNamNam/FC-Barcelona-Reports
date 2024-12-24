import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_events_df(all_events):
    """ Create DataFrame from input data"""
    logger.info("Creating DataFrame from events data.")
    return pd.DataFrame(all_events)

def ensure_required_columns(events_df, required_columns):
    """ Ensure all required columns exist in DataFrame, fill with default values if missing"""
    logger.info("Ensuring required columns exist in DataFrame.")
    for col, default_value in required_columns.items():
        if col not in events_df:
            logger.warning(f"Column {col} is missing. Filling with default value: {default_value}")
            events_df[col] = default_value
    return events_df.dropna(subset=['playerId'])

def extract_display_names(events_df, columns):
    """ Extract display names for dictionary columns"""
    logger.info("Extracting display names for specified columns.")
    for col in columns:
        events_df[col] = events_df[col].apply(lambda x: x['displayName'] if isinstance(x, dict) else x)
    return events_df

def convert_numeric_columns(events_df, numeric_columns):
    """ Convert specified columns to numeric, handle errors"""
    logger.info("Converting numeric columns.")
    for col in numeric_columns:
        events_df[col] = pd.to_numeric(events_df[col], errors='coerce').fillna(0).astype(float)
    return events_df

def convert_boolean_columns(events_df, boolean_columns):
    """ Convert specified columns to boolean"""
    logger.info("Converting boolean columns.")
    for col in boolean_columns:
        events_df[col] = events_df[col].astype(bool)
    return events_df

def calculate_total_seconds(events_df):
    """ Calculate total seconds from minutes and seconds columns"""
    logger.info("Calculating total seconds for each event.")
    events_df['total_seconds'] = events_df['minute'] * 60 + events_df['second']
    return events_df

def assign_passer_and_recipient(events_df):
    """ Assign passer and recipient for passing events"""
    logger.info("Assigning passer and recipient for passes.")
    events_df['passer'] = events_df.apply(lambda row: row['playerId'] if row['type'] == 'Pass' else None, axis=1)
    successful_passes = events_df[(events_df['type'] == 'Pass') & (events_df['outcomeType'] == 'Successful')].copy()
    successful_passes['recipient'] = successful_passes['playerId'].shift(-1)
    return pd.merge(
        events_df,
        successful_passes[['id', 'total_seconds', 'type', 'recipient']],
        how='left',
        on=['id', 'total_seconds', 'type']
    )

def finalize_events_df(events_df):
    """ Final adjustments: rename columns and set data types"""
    logger.info("Finalizing DataFrame with column renaming and data type adjustments.")
    events_df['passer'] = events_df['passer'].astype(pd.Int64Dtype())
    events_df['recipient'] = events_df['recipient'].astype(pd.Int64Dtype())
    events_df.rename(columns={
        'id': 'event_id', 'eventId': 'event_type_id', 'teamId': 'team_id', 'playerId': 'player_id',
        'outcomeType': 'type_outcome', 'endX': 'end_x', 'endY': 'end_y',
        'goalMouthZ': 'goal_mouth_z', 'goalMouthY': 'goal_mouth_y', 'isTouch': 'is_touch',
        'isShot': 'is_shot', 'isGoal': 'is_goal', 'cardType': 'card_type', 'isOwnGoal': 'is_own_goal'
    }, inplace=True)
    return events_df

def preprocess_events(all_events):
    logger.info("Starting event preprocessing pipeline.")
    required_columns = {
        'competition': None,
        'match_id': None,
        'id': None,
        'eventId': None,
        'minute': 0,
        'second': 0,
        'teamId': None,
        'period': None,
        'playerId': None,
        'type': None,
        'outcomeType': None,
        'x': 0.0,
        'y': 0.0,
        'endX': 0.0,
        'endY': 0.0,
        'goalMouthZ': 0.0,
        'goalMouthY': 0.0,
        'isTouch': False,
        'isShot': False,
        'isGoal': False,
        'cardType': None,
        'isOwnGoal': False
    }
    numeric_columns = ['minute', 'second', 'x', 'y', 'endX', 'endY', 'goalMouthZ', 'goalMouthY']
    boolean_columns = ['isTouch', 'isShot', 'isGoal', 'isOwnGoal']
    dict_columns = ['period', 'type', 'outcomeType', 'cardType']
    
    events_df = create_events_df(all_events)
    events_df = ensure_required_columns(events_df, required_columns)
    events_df = extract_display_names(events_df, dict_columns)
    events_df = convert_numeric_columns(events_df, numeric_columns)
    events_df = convert_boolean_columns(events_df, boolean_columns)
    events_df = calculate_total_seconds(events_df)
    events_df = assign_passer_and_recipient(events_df)
    events_df = finalize_events_df(events_df)

    logger.info("Event preprocessing pipeline completed.")
    return events_df
